from datetime import datetime

import scrapy


class HubSpiderSpider(scrapy.Spider):
    name = 'hub_spider'
    start_urls = ['https://hub.biz/Port-Hope-MI/']
    zyte_key = '13571d1e57eb4653b581bbb470b274f0'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'hub.biz.csv',
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
        for data in response.css('div.states-list a'):
            state_url = data.css('::attr(href)').get()
            yield response.follow(url=state_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('div.counties h2 a'):
            city_url = data.css('::attr(href)').get()
            yield response.follow(url=city_url, callback=self.parse_categories, headers=self.headers)

    def parse_categories(self, response):
        for data in response.css('div.name-lines a'):
            cate_url = data.css('::attr(href)').get()
            yield response.follow(url=cate_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('ul.card-listings li h2 a'):
            list_url = data.css('::attr(href)').get()
            yield response.follow(url=list_url, callback=self.parse_details, headers=self.headers)

        next_page = response.css('a.next-p::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_listing, headers=self.headers)

    def parse_details(self, response):
        item = dict()
        item['Business Name'] = response.css('h1[itemprop="name"] a::text').get('').strip()
        item['Street Address'] = response.css('p[itemprop="streetAddress"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['State'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Phone Number'] = response.css('p[itemprop="telephone"]::text').get('').strip()
        item['Latitude'] = response.css('meta[itemprop="latitude"]::attr(content)').get('').strip()
        item['Longitude'] = response.css('meta[itemprop="longitude"]::attr(content)').get('').strip()
        item['Source_URL'] = 'https://hub.biz/Port-Hope-MI/'
        item['Occupation'] = response.css('div.org h2.cat-in a::text').get('').strip()
        item['Lead_Source'] = 'hub.biz'
        item['Detail_Url'] = response.url
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item

