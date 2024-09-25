#import flask
from flask import Flask, request, jsonify, render_template, send_from_directory # Flask
from flask_cors import CORS

import ollama

app = Flask(__name__)

import mysql.connector
import json
import hashlib
import chromadb
from chromadb.config import Settings

from langchain.text_splitter import CharacterTextSplitter
from langchain.schema.document import Document
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
#from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_community.document_loaders import PyMuPDFLoader

import os
import mimetypes

try:
	conn = mysql.connector.connect(
		user="root",
		password="",
		host="127.0.0.1",
		port=3306,
		database="ollama"
	)
except: #mariadb.Error as e:
	print("Error connecting to DB")
	exit(1)
cur=conn.cursor()


# 定义允许的内网 IP 范围
#allowed_origins = ["http://192.168.28.{}".format(i) for i in range(1, 256)]

#CORS(app, resources={r"/*": {"origins": allowed_origins}})
CORS(app)

# 讀取 Model


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/bot')
def bot():
    # 讀取聊天室
    sql = "select chat_id, chat_name from user_chat where user_id = %s order by id desc;"
    cur.execute(sql,(1,))
    record = cur.fetchall()
    record1 = []
    for i in record:
        chat_name = i[1]
        if len(chat_name) > 15:
            chat_name = chat_name[:13]+"..."
        record1.append([i[0],chat_name])
    print("all_chat",record1)
    return render_template('bot.html', record=record1)
    #return send_from_directory('./templates', 'bot.html')

@app.route('/load_chat',methods=['POST']) # 讀取聊天記錄
def load_chat():
    data = request.get_json()
    chat_id = data['chat_id']
    print("chat_id",chat_id)
    sql = "select q_a from chat where JSON_EXTRACT(q_a, '$.chat_id') = %s;"
    cur.execute(sql,(chat_id,))
    q_a = []
    for i in cur.fetchall():
        q_a.append(json.loads(i[0]))
    print("q_a",q_a)
    return jsonify({'result': q_a})

# @app.route('/new_chat',methods=['POST'])
# def new_chat():
#     data = request.get_json()
#     user = data['user']
    
#     return jsonify({'chat_id': True})

# def load_vectorestore(): # 處理 RAG

def get_file_type(file_path): # 判斷檔案類型
    if not os.path.isfile(file_path):
        return "File does not exist"
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type == 'text/plain':
        return 'txt'
    elif mime_type == 'application/pdf':
        return 'pdf'
    else:
        return 'Unknown file type'

@app.route('/chat',methods=['POST']) # 使用者傳送聊天訊息
def chat():
    # 使用者傳送的訊息
    query = request.form.get('query') # 使用者問題
    chat_id = request.form.get('chat_id') # 聊天室 id
    user = request.form.get('user') # 使用者名稱
    user_id = request.form.get('user_id') # 使用者 id
    rag = False
    filename = ""
    if 'file' in request.files:
        rag = True
        file = request.files['file'] # 上傳檔案
        filename = file.filename
        file.save(os.path.join('file', user+"_"+file.filename))
    system_prompt = 'Please answer the question based on the language used by the user. If you determine that the language is Chinese, answer in Traditional Chinese.'
    messages = [{"role":"system","content":system_prompt}] # 聊天記錄
    
    # 載入聊天訊息
    first = False # 是否為新聊天
    if chat_id == "new_chat": # 新聊天
        first = True
        print('new_chat')
        # 用 hash 建 chat_name (user name + 使用者聊天室數量)
        sql = "select count(*) from user_chat,(SELECT id from user where name=%s) as a where user_id = a.id;"
        cur.execute(sql,(user,))
        record = cur.fetchall()[0]
        num = str(record[0])
        hash_object = hashlib.sha256((user+num).encode())
        chat_id = hash_object.hexdigest()
        # 新增聊天
        sql = "insert into user_chat(chat_id,user_id,chat_name) values (%s,%s,%s);"
        cur.execute(sql,(chat_id,user_id,"new_chat"))
        conn.commit()
    
    else: # 舊聊天
        print('old_chat')
        # 辨識聊天室 id -> 取得歷史對話紀錄
        sql = "select q_a from chat where JSON_EXTRACT(q_a, '$.chat_id') = %s and JSON_EXTRACT(q_a, '$.role') != 'file';"
        cur.execute(sql,(chat_id,))
        q_a = cur.fetchall()
        for i in q_a:
            messages.append(json.loads(i[0]))
    
    # 是否有 RAG
    retrieve_data = ""
    if rag == True: # 有 RAG
        print("RAG檔案")
        # chromadb
        client = chromadb.HttpClient(host='host.docker.internal', port=8000)
        # 新增 collection (name = chat_id + user name)
        collection_name = chat_id[:63]
        client.get_or_create_collection(collection_name)
        # embedding
        text_splitter = CharacterTextSplitter(chunk_size=100,chunk_overlap=20)
        if get_file_type("file/"+user+"_"+filename) == "txt":
            loader = TextLoader("file/"+user+"_"+filename, encoding="utf-8")
            documents = loader.load()
            docs = text_splitter.split_documents(documents)
        elif get_file_type("file/"+user+"_"+filename) == "pdf":
            loader = PyMuPDFLoader("file/"+user+"_"+filename)
            documents = loader.load()
            docs = text_splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(
            documents = docs,
            collection_name = collection_name,
            embedding = OllamaEmbeddings(model="mxbai-embed-large"),
            client = client
        )
        # retrieve
        retriever = vectorstore.as_retriever()
        results = retriever.invoke(query, limit=1)
        retrieve_data = results[0].page_content

        # 保存 RAG 檔案
        sql = "insert into chat(q_a) values (%s);"
        cur.execute(sql,(json.dumps({"role":"file","content":filename,"chat_id":chat_id},ensure_ascii=False),))
        conn.commit()
    else:
        # chromadb
        print("檢查RAG紀錄")
        client = chromadb.HttpClient(host='host.docker.internal', port=8000)
        collections = client.list_collections()
        collection_name = chat_id[:63]
        for collection in collections:
            if collection.name == collection_name: # 有 RAG 紀錄
                print("有RAG紀錄")
                vectorstore = Chroma(
                    collection_name = collection_name,
                    embedding_function = OllamaEmbeddings(model="mxbai-embed-large"),
                    client = client
                )
                # retrieve
                retriever = vectorstore.as_retriever()
                results = retriever.invoke(query, limit=1)
                retrieve_data = results[0].page_content
                rag = True
                break

    # 產生回覆
    if rag == True: # 有 RAG
        print("RAG回覆")
        # augmented
        system_prompt = f'Please using this data: {retrieve_data} to answer the question: {query} based on the language used by the user. If you determine that the language is Chinese, answer in Traditional Chinese.'
        messages[0]["content"] = system_prompt
        print("messages",messages)
        # generate
        response = ollama.chat(
            model="llama3",
            messages=messages
        )
        print(response)
        result = response["message"]["content"]
    else: # 沒 RAG
        print("無RAG")
        messages.append({"role":"user","content":query,"chat_id":chat_id})
        print("messages",messages)
        response = ollama.chat(
            model="llama3",
            messages=messages
        )
        print(response)
        result = response["message"]["content"]
    
    # 保存問題和回覆
    sql = "insert into chat(q_a) values (%s);"
    cur.execute(sql,(json.dumps({"role":"user","content":query,"chat_id":chat_id},ensure_ascii=False),))
    conn.commit()
    sql = "insert into chat(q_a) values (%s);"
    cur.execute(sql,(json.dumps({"role":"assistant","content":result,"chat_id":chat_id},ensure_ascii=False),))
    conn.commit()

    if first == True: # 新聊天
        # 產生聊天標題
        system_prompt = "Please generate a brief title for the question in the user's language based on their question."
        messages1 = [{"role":"system","content":system_prompt}, {"role":"user","content":query}]
        response = ollama.chat(
            model="llama3",
            messages=messages1
        )
        print(response)
        title = response["message"]["content"]
        sql = "update user_chat set chat_name=%s where chat_id=%s;"
        cur.execute(sql,(title,chat_id))
        conn.commit()
    
    # 回覆+標題傳回前端
    if first == True:
        print(first,jsonify({'result': result, 'chat_name': title}))
        return jsonify({'result': result, 'chat_name': title, 'chat_id': chat_id})
    else:
        print(first,jsonify({'result': result}))
        return jsonify({'result': result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)