# import ollama

# stream = ollama.chat(
#     model='llama3',
#     messages=[{'role': 'user', 'content': 'Why is the sky blue?'}],
#     stream=True,
# )

# for chunk in stream:
#   print(chunk['message']['content'], end='', flush=True)
import chromadb
client = chromadb.HttpClient(host='host.docker.internal', port=8000)

collections = client.list_collections()
for collection in collections:
    print(collection.name)
    #client.delete_collection(collection.name)
#print(collection.peek())