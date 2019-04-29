# -*- coding: utf-8 -*-
import scrapy
import requests
from tqdm import tqdm

class LogementsSpider(scrapy.Spider):
   pbar = tqdm (total=95, desc = 'dpt')
   name = 'logements'
   sitemap = 'http://www.fioulreduc.com/sitemap.xml/'

   @classmethod
   def from_crawler (cls, crawler, *args, **kwargs):
      spider = super(LogementsSpider, cls).from_crawler(crawler, *args, **kwargs)
      crawler.signals.connect(spider.item_scraped, signal=scrapy.signals.item_scraped)
      crawler.signals.connect(spider.item_scraped, signal=scrapy.signals.item_dropped)
      return spider

   def item_scraped(self, item, spider):
       self.pbar.update()

   def start_requests(self):
       r = requests.get(self.sitemap)
       response = scrapy.http.TextResponse(self.sitemap, body=r.text.encode())
       urls = response.xpath('//loc/text()').extract()
       departements = [url for url in urls if url.split('/')[-1].startswith('departement')]
       for departement in departements[:2]:
           r = scrapy.Request(url=departement, callback=self.parse)
           yield r

   def parse(self, response):
       textes = response.xpath('//*/text()').extract()
       villes = [texte for texte in textes if texte.startswith('http')]

       departement_dict = {}
       results = []
       for url in villes[:10]:
           request = requests.get(url)
           r = scrapy.http.TextResponse(self.sitemap, body=request.text.encode())
           selector = '//div[@class="part-inte"]//p/text()'
           paragraphes = r.xpath(selector).extract()
           stats = [paragraphe for paragraphe in paragraphes if paragraphe.startswith('A ')]
           departement_dict['logements'] = stats[0].split('environ')[1].split()[0]
           departement_dict['url'] = url
           departement_dict['ville'] = stats[0].split()[1].split(',')

           results.append(departement_dict.copy())

       return results