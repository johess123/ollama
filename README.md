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
 - Flask
   - Python 的網頁後端框架。
   - 由於 Ollama 提供 Python SDK，透過 Flask 快速建立可與 LLM 交互的系統。

 <h2>使用方法</h2>
 
 - 安裝 Ollama
 - 透過 Ollama 下載 LLM Model
 - 部署 Flask, MySQL, ChromaDB
 - 在要嵌入聊天機器人的網頁前端，透過 JavaScript 嵌入聊天機器人。

 <h2>未來展望</h2>
 
 - 透過 docker 打包整個架構，方便使用者快速部署。
 - 提升聊天機器人產生的回覆的精準度。
