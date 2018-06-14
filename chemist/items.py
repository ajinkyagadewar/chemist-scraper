# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class ChemistItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    site_chemist_url = scrapy.Field()
    address = scrapy.Field()
    address2 = scrapy.Field()
    city = scrapy.Field()
    state = scrapy.Field()
    country = scrapy.Field()
    zip = scrapy.Field()
    phone = scrapy.Field()
    email = scrapy.Field()
    cell = scrapy.Field()
    hours_of_operation = scrapy.Field()
    mode_of_payment = scrapy.Field()
    keywords = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    jd_verified = scrapy.Field()
