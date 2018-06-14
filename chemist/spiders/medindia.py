# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from chemist.items import ChemistItem

class MedindiaSpider(scrapy.Spider):
    name = "medindia"
    allowed_domains = ["medindia.net"]
    start_urls = (
                  'http://www.medindia.net/buy_n_sell/chemist/chemist_result.asp?alpha=A',
                  )
    rules = (
             Rule(LinkExtractor(allow=('\?alpha=[A-Z]', )), callback='parse'),
             )
    
    def parse(self, response):
        sel = Selector(response)
        chemists = sel.xpath('//div[@class="article-content"]//p[@class="name"]//a/@href').extract()
        next_page_url = sel.xpath('//div[@class="pagination"]').re('class="active">\d+</a>\s*<a href="([^"]*)"')

        for chemist in chemists:
            item_url = 'http://www.medindia.net/buy_n_sell/chemist/' + chemist
            yield scrapy.Request(item_url, callback=self.parse_item)
            
        if next_page_url:            
            yield scrapy.Request(next_page_url[0].strip(), callback=self.parse)

    def parse_item(self, response):
#        item = ChemistItem()
        content = response.xpath('//div[@class="article-content big-fonts"]').re('javascript:googlemap\([^\)]*');
        id = response.xpath('//div[@class="article-content big-fonts"]').re('javascript:contactdetails\([^\)]*');
        
        # Get Other Contact Details
        contact_url = 'www.medindia.net/buy_n_sell/chemist/chemist_contact_details.asp?id=' + id[0]
        item = yield scrapy.Request(contact_url, callback=self.parse_item)
        
        data = content.split("'");
        address = data[1].split("|")
        zip = address[2].split("-")
        
        item['name'] = data[2]
        item['address'] = address[0]
        item['address2'] = address[1]
        item['city'] = zip[0]
        item['state'] = address[3]
        item['zip'] = zip[1]
        item['contact_person'] = ''
        item['fax'] = ''
        item['phone'] = response.xpath('//div[@class="inner clearfix"]').re('<strong>Phone</strong>[^<]*<span>([^<]*)</span>')
        item['email'] = response.xpath('//div[@class="inner clearfix"]').re('<strong>E-Mail</strong>[^<]*<span>([^<]*)</span>')
        item['site_chemist_url'] = response.url
        item['country'] = ['India']
        item['cell'] = ''
        
        for key, value in item.iteritems():
            if len(item[key]) > 0:
                item[key] = item[key][0]
            else:
                item[key] = "NULL"
        print item
    
    def parse_contact_details(self, response):
        item = ChemistItem()
        item['phone'] = response.xpath('//table').re('Phone\d+\s*</td>[^>]*>:</td>[^>]*>([^<]*)</td>')
        return item
 