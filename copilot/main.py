
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pgvector.psycopg2 import register_vector
from openai import OpenAI


import os
import numpy as np
import psycopg2
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

load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')

openai_client =  OpenAI(
    api_key=openai_api_key, 
)

conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST'),
    database=os.getenv('POSTGRES_DB'),
    user=os.getenv('POSTGRES_USER'),
    password=os.getenv('POSTGRES_PASSWORD'),
)
register_vector(conn)

def getEmbedding(text: str):
    return openai_client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    ).data[0].embedding

def getContextFromDB(embedding):
    embedding = np.array(embedding)
    cur = conn.cursor()
    try:
        cur.execute("SELECT url, text FROM retailer_pages_embeddings ORDER BY embedding <-> %s LIMIT 40;", (embedding,))
        results = cur.fetchall()
    except psycopg2.Error as e:
        print(f"Error: {e}")
    
    urls = set()
    context = []
    for row in results:
        urls.add(row[0])
        context.append(row[1])
    return urls, '.'.join(context)

def get_completion_from_context(context, query, model="gpt-4o", temperature=0, max_tokens=1000):
    
    delimiter = "```"

    overarching_prompt = f"""
    You are a friendly chatbot.\
    You can answer questions based on provided information 
    """

    messages = [
        {"role": "system", "content": overarching_prompt},
        {"role": "user", "content": f"{delimiter}{query}{delimiter}"},
        {"role": "assistant", "content": f"Relevant information: \n {context}"}   
    ]

    response = openai_client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    return response.choices[0].message.content
    
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
            query_embed = getEmbedding(data)
            urls, context = getContextFromDB(query_embed)

            response = get_completion_from_context(context, data) 
            
            chat_history.append({"role": "assistant", "content": str(response)})
            await websocket.send_text(str(response))
            await websocket.send_text("Sourced from: \n" + ',\n'.join(urls))

        except Exception as e:
            print(f"Error: {e}")
            break


# 6. Run the API
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
