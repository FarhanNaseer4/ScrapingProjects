from datetime import datetime

import scrapy


class PunchbowlSpiderSpider(scrapy.Spider):
    name = 'punchbowl_spider'
    start_urls = ['https://www.punchbowl.com/vendors/flower-shops']
    zyte_key = '13571d1e57eb4653b581bbb470b274f0'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'punchbowl.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date', 'Meta_Description'],
        'HTTPERROR_ALLOW_ALL': True,
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('li.state a'):
            state_url = data.css('::attr(href)').get()
            if state_url:
                yield response.follow(url=state_url, callback=self.parse_county, headers=self.headers)

    def parse_county(self, response):
        for data in response.css('li.city a'):
            county_url = data.css('::attr(href)').get()
            if county_url:
                yield response.follow(url=county_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('li.vendor-list-entry a.vendor-list-entry__name'):
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.org::text').get('').strip()
        item['Street Address'] = response.css('p.street-address::text').get('').strip()
        item['State'] = response.css('span.region::text').get('').strip()
        item['Zip'] = response.css('p.postal-code::text').get('').strip()
        item['Phone Number'] = response.css('p.phone_number::text').get('').strip()
        item['Business_Site'] = response.css('div.detail-website a::attr(href)').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://www.punchbowl.com/vendors/flower-shops'
        item['Lead_Source'] = 'punchbowl'
        item['Occupation'] = 'Flower Shop'
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item['Meta_Description'] = 'Send the freshest flowers from a local flower shop.'
        yield item
