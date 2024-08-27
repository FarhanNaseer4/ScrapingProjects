from datetime import datetime

import scrapy


class BestwineriesSpiderSpider(scrapy.Spider):
    name = 'bestwineries_spider'
    start_urls = ['https://bestwineries.org/']
    custom_settings = {
        'FEED_URI': 'bestwineries.csv',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.state-towns p a'):
            state_url = data.css('::attr(href)').get()
            if state_url:
                yield response.follow(url=state_url, callback=self.parse_county, headers=self.headers)

    def parse_county(self, response):
        for data in response.css('ul.list-unstyled a'):
            county_url = data.css('::attr(href)').get()
            if county_url:
                yield response.follow(url=county_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.col-lg-12 h3 a'):
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.title::text').get('').strip()
        item['Street Address'] = response.css('div.address::text').get('').strip()
        item['State'] = response.css('div.location span:nth-child(2)::text').get('').strip()
        item['Zip'] = response.css('div.location span:nth-child(3)::text').get('').strip()
        item['Phone Number'] = response.css('div.detail-phone::text').get('').strip()
        item['Business_Site'] = response.css('div.detail-website a::attr(href)').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://bestwineries.org/'
        item['Lead_Source'] = 'bestwineries'
        item['Occupation'] = 'Winery'
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item['Meta_Description'] = 'Best Local Wineries and Tours near me'
        yield item
