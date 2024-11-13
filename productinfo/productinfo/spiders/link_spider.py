import scrapy
import re
# Actually is the LxmlLinkExtractor
from bs4 import BeautifulSoup
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from productinfo.items import ProductInfoItem

class LinkSpider(CrawlSpider):
    name = "link"

    def __init__(self, domain='', regex='', *args, **kwargs):
        super(LinkSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = [domain]
        self.start_urls = [f'https://{domain}']
        self.visited_urls = set()

    # Under the hood, the CrawlSpider is extracting all links and creating a request for each of them,
    # with the call back specified here.
    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        if response.url not in self.visited_urls:
            self.visited_urls.add(response.url)
            # Only process if the url is of a product
            if re.search('www.bearmattress.com/product.*', response.url):
                soup = BeautifulSoup(response.body, 'lxml')
                images = soup.find('section', class_='product-slider').find_all('div', class_='product-slider__controls-thumb')
                image_arr = []
                for image in images:
                    image_arr.append({
                        'title': image['alt'],
                        'url:' : image['style']
                        })
                description = ""
                description_elem = soup.find('div', class_='product-content')
                if description_elem:
                    description = description_elem.text
                ## TODO(mkedia): Need to verify if this works.
                for script in soup(["script", "style"]):
                  script.extract()
                html_text = soup.get_text()
                product = ProductInfoItem()

                product['url']=response.url
                product['html']= html_text
                product['name']= soup.h1.text
                #'description': soup.find('div', class_='cs-description').text,
                product['description']= description
                product['discount_price'] = soup.find('div', class_='discount-price').find("span", id='discount-price').text
                product['total_price'] = soup.find('div', class_='total-price').find("span", id='total-price').text
                product['currency']= soup.find('div', class_='discount-price').find("span", class_='last').text
                product['images']= image_arr
                yield product
