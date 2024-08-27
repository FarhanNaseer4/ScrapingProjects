import json

import scrapy


class MoraineSpiderSpider(scrapy.Spider):
    name = 'moraine_spider'
    request_api = 'https://campusdirectory.morainevalley.edu/api/employees?find={}&criteria=firstname'
    first_name = ['a', 'b', 'c', 'd', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't','u', 'v', 'w', 'x', 'y', 'z']
    custom_settings = {
        'FEED_URI': 'moraine_data.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
    }
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',

    }

    def start_requests(self):
        for first in self.first_name:
            yield scrapy.Request(url=self.request_api.format(first), callback=self.parse, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.body)
        if result:
            for data in result:
                item = dict()
                item['Full Name'] = data.get('firstName', '') + ' ' + data.get('lastName', '')
                item['First Name'] = data.get('firstName', '')
                item['Last Name'] = data.get('lastName', '')
                item['Business Name'] = data.get('department', '')
                item['Occupation'] = data.get('title', '')
                item['Phone Number'] = data.get('fullOfficeNumber', '')
                item['Source_URL'] = 'https://www.morainevalley.edu/'
                item['Lead_Source'] = 'morainevalley'
                yield item
