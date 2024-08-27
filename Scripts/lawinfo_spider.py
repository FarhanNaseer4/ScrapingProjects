from datetime import datetime

import scrapy


class LawinfoSpiderSpider(scrapy.Spider):
    name = 'lawinfo_spider'
    start_urls = ['https://www.lawinfo.com/by-location/']
    zyte_key = '13571d1e57eb4653b581bbb470b274f0'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'lawinfo.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date'],
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

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, headers=self.headers)

    def parse(self, response):
        for data in response.css('section.state-list li a'):
            state_url = data.css('::attr(href)').get()
            yield response.follow(url=state_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.xpath('//h2[contains(text(),"All Cities")]//following::ul[contains(@class,'
                                   '"location-links")]/li/a'):
            city_url = data.xpath('./@href').get()
            yield response.follow(url=city_url, callback=self.parse_categories, headers=self.headers)

    def parse_categories(self, response):
        for data in response.css('h3.card-header a'):
            cate_url = data.css('::attr(href)').get()
            yield response.follow(url=cate_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.firm_name_container h2 a'):
            list_url = data.css('::attr(href)').get()
            yield response.follow(url=list_url, callback=self.parse_details, headers=self.headers)

    def parse_details(self, response):
        item = dict()
        item['Business Name'] = response.css('div[id="headerTitle"] h1::text').get('').strip()
        item['Category'] = ''.join(data.css('::text').get('') for data in response.css('p.listing-details-tagline span'))
        item['Street Address'] = response.css('p.listing-desc-address span.street-address::text').get('').strip()
        item['Zip'] = response.css('p.listing-desc-address span.postal-code::text').get('').strip()
        item['State'] = response.css('p.listing-desc-address span.region::text').get('').strip()
        item['Phone Number'] = response.css('a.listing-desc-phone::text').get('').strip()
        item['Business_Site'] = response.css('a.profile-website-header::attr(href)').get('').strip()
        item['Source_URL'] = 'https://www.lawinfo.com/by-location/'
        item['Occupation'] = 'Attorney'
        item['Lead_Source'] = 'lawinfo'
        item['Detail_Url'] = response.url
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item
