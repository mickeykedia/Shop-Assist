
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from llama_index.core import VectorStoreIndex, Settings, Document
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


import os
import json

app = FastAPI()

origins = [
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,  # If you need to send cookies
    allow_methods=["*"],    # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)

# 1. Load your data
## TODO(mkedia): Replace with pg 
with open('../data/products.json', 'r') as f:
    data = json.load(f)


documents = []
for product in data:
    # TODO(mkedia): 
    #   Add price / images
    #   Add full HTML 
    doc = Document(
            text=product['html'],
            metadata={'name':product['name'], 'url':product['link']})
    documents.append(doc)

# 2. Initialize LLM and ServiceContext
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
Settings.llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=openai_api_key)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

# 3. Create a LlamaIndex index
index = VectorStoreIndex.from_documents(documents, embed_model=Settings.embed_model, similarity_top_k=100)
query_engine = index.as_query_engine(llm=Settings.llm)

# 4. Define the chat API endpoint
class ChatMessage(BaseModel):
    message: str

@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    chat_history = []  # Store the conversation history

    while True:
        try:
            data = await websocket.receive_text()
            chat_history.append({"role": "user", "content": data}) 

            # Construct the query with chat history
            query_str = " ".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
            response = query_engine.query(query_str)
            
            chat_history.append({"role": "assistant", "content": str(response)})
            sources = set([source['url'] for source in response.metadata.values()])
            await websocket.send_text(str(response))
            await websocket.send_text("Sourced from: " + ','.join(sources))

        except Exception as e:
            print(f"Error: {e}")
            break


# 5. Simple HTML for the chat interface
html = """
<!DOCTYPE html>
<html>
<head>
    <title>Chat with LlamaIndex</title>
</head>
<body>
    <h1>Chat with LlamaIndex</h1>
    <input type="text" id="messageBox" autocomplete="off" placeholder="Type your message here..." />
    <button onclick="sendMessage()">Send</button>
    <div id="chatbox"></div>
    <script>
        var websocket = new WebSocket("ws://localhost:8000/chat");
        websocket.onmessage = function(event) {
            document.getElementById('chatbox').innerHTML += '<p><b>Assistant:</b> ' + event.data + '</p>';
        };
        function sendMessage() {
            var messageBox = document.getElementById('messageBox');
            websocket.send(messageBox.value);
            document.getElementById('chatbox').innerHTML += '<p><b>You:</b> ' + messageBox.value + '</p>';
            messageBox.value = '';
        }
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# 6. Run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
