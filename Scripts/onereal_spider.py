import json

import scrapy


class OnerealSpiderSpider(scrapy.Spider):
    name = 'onereal_spider'
    request_api = 'https://bff.therealbrokerage.com/api/v1/runway/agents/search?name=a&pageNumber={}&pageSize=20'
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    }

    custom_settings = {
        'FEED_URI': 'onereal.csv',
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

    def start_requests(self):
        item = {'page': 1}
        yield scrapy.Request(url=self.request_api.format(1), meta={'item': item},
                             callback=self.parse, headers=self.headers)

    def parse(self, response):
        keys = response.meta['item']
        result = json.loads(response.body)
        agent_data = result.get('agents', [])
        for personal_info in agent_data:
            item = dict()
            address_data = personal_info.get('addresses', [])
            for data in address_data:
                item['State'] = data.get('stateOrProvince', '')
                item['Zip'] = data.get('zipOrPostalCode', '')
                item['Street Address'] = data.get('streetAddress1', '')
            item['Phone Number'] = personal_info.get('phoneNumber', '')
            item['First Name'] = personal_info.get('firstName', '')
            item['Last Name'] = personal_info.get('lastName', '')
            item['Full Name'] = item['First Name'] + ' ' + item['Last Name']
            item['Occupation'] = 'Realtor'
            item['Source_URL'] = 'https://www.onereal.com/search-agent?search_label=a&search_by=AGENT'
            item['Lead_Source'] = 'onereal'
            yield item
        has_more = result.get('hasMore', '')
        if has_more:
            page = keys.get('page') + 1
            keys['page'] = page
            yield scrapy.Request(url=self.request_api.format(page), meta={'item': keys},
                                 callback=self.parse, headers=self.headers)
