import csv
from datetime import datetime

import scrapy


class LocatorApaSpiderSpider(scrapy.Spider):
    name = 'locator_apa_spider'
    request_url = 'https://locator.apa.org/resultsS/1/{}'
    custom_settings = {
        'FEED_URI': 'locator_apa.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date']
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_state = self.get_search_state()

    def get_search_state(self):
        with open('state_name.csv', 'r', encoding='utf-8-sig') as reader:
            return list(csv.DictReader(reader))

    def start_requests(self):
        for data in self.request_state:
            state = data.get('states', '')
            yield scrapy.Request(url=self.request_url.format(state), callback=self.parse, headers=self.headers)

    def parse(self, response):
        for data in response.css('div.media-body a.media-profile-pic'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        fullname = response.css('h3.panel-title::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Street Address'] = response.css('span.street-address::text').get('').strip()
        item['State'] = response.css('span.region::text').get('').strip()
        item['Zip'] = response.css('span.postal-code::text').get('').strip()
        item['Phone Number'] = response.css('a.list-group-item div.tel::text').get('').strip()
        item['Business_Site'] = response.xpath('//i[contains(@class,"fa-globe")]/following-sibling::text()').get('').strip()
        item['Category'] = ','.join(data.css('::text').get('') for data in response.css('div[id="pract_area"] ul li'))
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://locator.apa.org/'
        item['Lead_Source'] = 'locator.apa'
        item['Occupation'] = 'Corporate Member'
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item

