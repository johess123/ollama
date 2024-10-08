<h1>可快速部署至網頁的本地 AI 機器人</h1>

<h2>構想</h2>

- 為了解決某些公司或個人想在自己的網頁嵌入 AI 聊天機器人，卻又不想承擔機密資料可能外洩給 Openai 等生成式 AI 公司的風險，並同時方便部署方式，能夠只透過一行指令嵌入網頁。

- 基於以上基礎，另外也透過 RAG，提供打造專屬公司或個人 AI 機器人的功能。

<h2>架構</h2>
 <img src="https://hackmd.io/_uploads/SJ5N8NWC0.png"/>
 
 - Ollama
   - 可在本地架設 LLM Model 的開源軟體。
   - 提供 Python SDK。
 
 - LangChain & ChromaDB
   - LangChain
     - 讓開發者可以更容易、有效地利用 LLM 的開源框架。
     - 可讓 LLM 擁有記憶功能。
   - ChromaDB
     - 向量資料庫，儲存 RAG 處理後的資料。
   - LangChain 搭配 ChromaDB 實作 RAG，可實現打造個人機器人的功能。
