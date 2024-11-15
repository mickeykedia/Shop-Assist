
from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from llama_index.core import VectorStoreIndex, Settings
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.postgres import PGVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from pydantic import BaseModel

import os
import numpy as np
import openai

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

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
Settings.llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=openai_api_key)
# Has to be aligned with productinfo/productinfo/pipelines.py
Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")

vector_store = PGVectorStore.from_params(
    database=os.getenv('POSTGRES_DB'),
    host=os.getenv('POSTGRES_HOST'),
    password=os.getenv('POSTGRES_PASSWORD'),
    port=5432,
    user=os.getenv('POSTGRES_USER'),
    # TODO(mkedia): Pass this as an argument from the command line
    table_name="bear_mattress",
    embed_dim=1536,
    hnsw_kwargs={
        "hnsw_m": 16,
        "hnsw_ef_construction": 64,
        "hnsw_ef_search": 40,
        "hnsw_dist_method": "vector_cosine_ops",
    },
)
vector_index = VectorStoreIndex.from_vector_store(vector_store=vector_store, embed_model=Settings.embed_model)
query_engine = vector_index.as_query_engine(llm=Settings.llm)

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
            await websocket.send_text("Sourced from: \n" + ',\n'.join(sources))

        except Exception as e:
            print(f"Error: {e}")
            break


# 6. Run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
