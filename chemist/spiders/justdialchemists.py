# -*- coding: utf-8 -*-
import MySQLdb
from chemist.items import ChemistItem
import pprint
import scrapy
from scrapy.selector import Selector
import re

db = MySQLdb.connect("localhost", "root", "ajinkya", "mydb")
cursor = db.cursor()
    
class JustDialChemistsSpider(scrapy.Spider):
    name = "justdialchemists"
    allowed_domains = ["justdial.com"]
    urls = []
        
    cursor.execute("SELECT name FROM mydb.location where parent_id in (SELECT location_id FROM mydb.location where parent_id=100)")
    cities = cursor.fetchall()

    for city in cities:
        cityurl = 'http://www.justdial.com/' + city[0] + '/Chemists'
        urls.append(cityurl)
        
    start_urls = urls
    
    def parse(self, response):
        sel = Selector(response)
        
        chemists = sel.xpath('//span[@class="jcn dcomclass"]//a/@href').extract()
        if len(chemists) <= 0:
            chemists = sel.xpath('//span[@class="jcn "]//a/@href').extract()
        
        next_page_url = sel.xpath('//div[@id="srchpagination"]').re('class="act">\d+</span>\s*<a href="([^"]*)"')
    
        for chemist in chemists:
            yield scrapy.Request(chemist, callback=self.parse_item)

        if next_page_url:            
            yield scrapy.Request(next_page_url[0].strip(), callback=self.parse)
    
    def parse_item(self, response):
        item = ChemistItem()
        content = response.xpath('//span[@class="jaddt"]/text()').extract()
        city_content = response.url.split("/")
        item['city'] = [city_content[3]]

        # Get state
        cursor.execute("SELECT name FROM mydb.location where \
            location_id = (SELECT parent_id FROM mydb.location \
            where name = %s limit 1)", item['city'])
        try:
            result = cursor.fetchone()[0]
        except:
            result = ''
        if result:
            item['state'] = [result]
        else:
            city_content = response.request.headers.get('Referer')
            cursor.execute("SELECT name FROM mydb.location where \
            location_id = (SELECT parent_id FROM mydb.location where \
            name = %s limit 1)", [city_content[3]])
            result = cursor.fetchone()[0]
            item['state'] = [result]

        if content:
            data = content[-1].split(",")
            zip_obj = [re.findall(r"(\d{6})", content[-1])]
            try:
                item['zip'] = zip_obj[0]
            except AttributeError as ae:
                item['zip'] = ''
                print str(ae)

            if data:
                item['address'] = [data[0]]
                item['address2'] = [content[-1].replace(data[0], "")]

        item['name'] = response.xpath('//span[@id="breadcrumbSpan"]/text()').extract()
        item['country'] = ['India']

        item['phone'] = response.xpath('//section[@class="moreinfo"]').re('class="ic_phn"></span><a class="tel"[^>]*>([^<]*)')
        if item['phone'] and item['phone'][0] == '':
            item['phone'] = response.xpath('//section[@class="moreinfo"]').re('class="ic_phn"></span><a class="tel"[^>]*><b>([^<]*)')

        item['cell'] = response.xpath('//section[@class="moreinfo"]').re('class="ic_mob"></span><a class="tel"[^>]*>([^<]*)')
        if item['cell'] and item['cell'][0] == '':
            item['cell'] = response.xpath('//section[@class="moreinfo"]').re('class="ic_mob"></span><a class="tel"[^>]*><b>([^<]*)')

        item['hours_of_operation'] = response.xpath('//div[@class="hrsop"]').re('<td>[^>]*>(.*)</td>')
        item['email'] = ''
        item['mode_of_payment'] = ['Cash']
        
        #  Other details
        keywords = [re.findall(r'<meta name="keywords" content="([^"]*)"', response.body, re.S)]
        try:
            item['keywords'] = keywords[0]
        except AttributeError as ae:
            item['keywords'] = ''
            
        latitude = [re.findall(r'name=\'lat_b\' value="([^"]*)"', response.body, re.S)]
        try:
            item['latitude'] = latitude[0]
        except AttributeError as ae:
            item['latitude'] = ''
            
        longitude = [re.findall(r'name=\'lng_b\' value="([^"]*)"', response.body, re.S)]
        try:
            item['longitude'] = longitude[0]
        except AttributeError as ae:
            item['longitude'] = ''
            
        jd_verified = [re.findall(r'\'(jvrp)\'', response.body, re.S)]
        try:
            item['jd_verified'] = jd_verified[0]
        except AttributeError as ae:
            item['jd_verified'] = ''

        for key, value in item.iteritems():
            if len(item[key]) > 0:
                item[key] = item[key][0]
                item[key] = re.sub("\t", "", item[key])
            else:
                item[key] = "NULL"

        item['site_chemist_url'] = response.url
        return item
