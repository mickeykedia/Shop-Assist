# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2
import os
from openai import OpenAI

from dotenv import load_dotenv
from itemadapter import ItemAdapter
from pgvector.psycopg2 import register_vector

def split_text(text:str, chunk_size: int=500):
    sentences = text.replace('\n', ' ').split('. ')
    chunks = []
    current_chunk = []
    current_size = 0
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if not sentence.endswith('.'):
            sentence += '.'
        sentence_size = len(sentence)

                # Check if adding this sentence would exceed chunk size
        if current_size + sentence_size > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sentence]
            current_size = sentence_size
        else:
            current_chunk.append(sentence)
            current_size += sentence_size
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def process_document(html: str, url: str):
    # Split into chunks
    chunks = split_text(html)

    # Prepare metadata
    metadatas = [{"url": url, "chunk": i} for i in range(len(chunks))]
    ids = [str(i) for i in range(len(chunks))]

    return ids, chunks, metadatas

class ProductInfoPipeline(object):
    def __init__(self):
        load_dotenv()
        self.conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST'),
            database=os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_USER'),
            password=os.getenv('POSTGRES_PASSWORD'),
        )
        register_vector(self.conn)
        self.cur = self.conn.cursor()
        self.openai_client =  OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), 
        )


    def process_item(self, item, spider):
        try: 
            self.cur.execute("INSERT INTO retailer_pages (retailer_id, url, html) VALUES (%s, %s, %s)", 
                (1, item['url'], item['html']))
            self.conn.commit()
        except psycopg2.Error as e:
            print(f"Error: {e}")
        ids, chunks, metadatas = process_document(item['html'], item['url'])
        for i in range(len(ids)):

            embedding = self.openai_client.embeddings.create(
                input=chunks[i],
                model="text-embedding-3-small"
            ).data[0].embedding
            try: 
                self.cur.execute("INSERT INTO retailer_pages_embeddings (retailer_id, text_id, url, text, embedding) VALUES (%s, %s, %s, %s, %s)", 
                    (1, ids[i], item['url'], chunks[i], embedding))
                self.conn.commit()
            except psycopg2.Error as e:
                print(f"Error: {e}")
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
