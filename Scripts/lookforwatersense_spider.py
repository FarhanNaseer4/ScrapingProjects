import json

import scrapy


class LookforwatersenseSpiderSpider(scrapy.Spider):
    name = 'lookforwatersense_spider'
    request_api = 'https://lookforwatersense.epa.gov/api/pros/?offset=0&limit=1500&zipCode=&zipCodeRadius=&availableForHire=Yes'
    custom_settings = {
        'FEED_URI': 'lookforwatersense.csv',
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
        'Accept': 'application/json',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_api, callback=self.parse, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.body)
        for row in result.get('rows', []):
            item = dict()
            item['First Name'] = row.get('firstName', '')
            item['Last Name'] = row.get('lastName', '')
            item['Full Name'] = row.get('fullName', '')
            item['Business Name'] = row.get('companyName', '')
            item['Street Address'] = row.get('address', '')
            item['State_Abrv'] = row.get('state', '')
            item['Zip'] = row.get('zipCode', '')
            item['Business_Site'] = row.get('webSite', '')
            item['Phone Number'] = row.get('phoneNumber', '')
            item['Email'] = row.get('email', '')
            item['Category'] = row.get('customerTypes', '')
            item['Source_URL'] = 'https://lookforwatersense.epa.gov/pros/'
            item['Lead_Source'] = 'lookforwatersense'
            item['Occupation'] = 'Certified Professionals'
            yield item
