# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class ProductInfoItem(scrapy.Item):
    url = scrapy.Field()
    html = scrapy.Field()
    name = scrapy.Field()
    description = scrapy.Field()
    discount_price = scrapy.Field()
    total_price = scrapy.Field()
    currency = scrapy.Field()
    images = scrapy.Field()
