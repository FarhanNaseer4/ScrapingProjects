from datetime import datetime

import scrapy


class CrepehouseSpiderSpider(scrapy.Spider):
    name = 'crepehouse_spider'
    start_urls = ['https://crepehouse.ca/']
    zyte_key = '3a51aa1571ca480e8d2f096496312751'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'HTTPERROR_ALLOW_ALL': True,
        'FEED_URI': 'crepehouse_meta.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date', 'Meta_Description']
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('li.c-list__item a'):
            list_url = data.css('::attr(href)').get()
            if list_url:
                yield response.follow(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('a.popular-item-category'):
            item = dict()
            item['Business Name'] = data.css('div.p-item__name::text').get('').strip()
            item['Occupation'] = data.css('div.p-item__category p::text').get('').strip()
            item['Meta_Description'] = response.xpath(
                '//meta[@name="description" or @property="og:description"]/@content').get('').strip()
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail,
                                      meta={'item': item}, headers=self.headers)

    def parse_detail(self, response):
        item = response.meta['item']
        address = response.xpath('//i[contains(@class,"fa-map-marker-alt")]/following-sibling::text()').get('').strip()
        if address:
            item['Street Address'] = address.split(',')[0].strip()
            state = address.split(',')[-1].strip()
            if state:
                item['State'] = state.split(' ')[0].strip()
                item['Zip'] = state.split(' ')[-1].strip()
        item['Phone Number'] = response.xpath('//a[contains(@href,"tel:")]/text()').get('').strip()
        item['Business_Site'] = response.xpath('//i[contains(@class,"fa-link")]/following-sibling::a/@href').get('').strip()
        item['Source_URL'] = 'https://crepehouse.ca/'
        item['Lead_Source'] = 'crepehouse'
        item['Detail_Url'] = response.url
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item



