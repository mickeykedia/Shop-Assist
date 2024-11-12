# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2
import os

from dotenv import load_dotenv
from itemadapter import ItemAdapter
from pgvector.psycopg2 import register_vector


class ProductinfoPipeline(object):
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

    def process_item(self, item, spider):
        self.cur.execute("")
        return item
