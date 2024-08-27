import csv
import json
from datetime import datetime

import scrapy


class HealthSpiderSpider(scrapy.Spider):
    name = 'health_spider'
    # start_urls = ['https://health.usnews.com/doctors/location-index']
    request_api = 'https://health.usnews.com/health-care/doctors/search-data?distance=in-state&location={}&page_num={}'
    custom_settings = {
        'FEED_URI': 'health_usnews.csv',
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
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_key = self.get_search_urls()

    def get_search_urls(self):
        with open('states.csv', 'r', encoding='utf-8-sig') as reader:
            return list(csv.DictReader(reader))

    def start_requests(self):
        for state in self.request_key:
            item = dict()
            item['State'] = state.get('States', '')
            yield scrapy.Request(url=self.request_api.format(state.get('States', ''), 1), meta={'item': item},
                                 callback=self.parse, headers=self.headers)

    def parse(self, response):
        p_item = response.meta['item']
        result = json.loads(response.body)
        matches = result.get('doctor_search', '').get('results', {}).get('doctors', {}).get('matches', [])
        if matches:
            for data in matches:
                item = dict()
                item['Full Name'] = data.get('full_name', '')
                item['First Name'] = data.get('first_name', '')
                item['Last Name'] = data.get('last_name', '')
                item['Description'] = data.get('blurb', '')
                item['Street Address'] = data.get('location', {}).get('street_address', '')
                item['Zip'] = data.get('location', {}).get('zip_code', '')
                item['State'] = data.get('location', {}).get('state', '')
                item['Phone Number'] = data.get('phone', '')
                item['Business Name'] = data.get('affiliated_hospital', '')
                item['Category'] = data.get('specialty', '')
                item['Source_URL'] = 'https://health.usnews.com/doctors/location-index'
                item['Occupation'] = 'Doctor'
                item['Lead_Source'] = 'health.usnews'
                item['Detail_Url'] = response.url
                item['Record_Type'] = 'Person'
                item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                yield item

        next_page = result.get('doctor_search', '').get('results', {}).get('doctors', {}).get('hasNextPage', '')
        if next_page:
            current_page = result.get('doctor_search', '').get('results', {}).get('doctors', {}).get('page_num', '')
            yield scrapy.Request(url=self.request_api.format(p_item.get('State', ''), current_page + 1),
                                 meta={'item': p_item}, callback=self.parse, headers=self.headers)
