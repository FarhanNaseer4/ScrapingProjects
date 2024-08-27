import json
from datetime import datetime

import scrapy


class LongandfosterSpiderSpider(scrapy.Spider):
    name = 'longandfoster_spider'
    request_api = 'https://www.longandfoster.com/include/ajax/api.aspx?op=SearchAgents&firstname=&lastname=&page={}&pagesize=200'
    base_url = 'https://www.longandfoster.com/AgentSearch/{}'
    custom_settings = {
        'FEED_URI': 'longandfoster.csv',
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
        'authority': 'www.longandfoster.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'cookie': 'BrokerOffice_Session=SessionCookie=70f5c1b0-ddcb-4c4c-9328-d05e3986375f; _gcl_au=1.1.1595813223.1666868931; rBW-ListingSearch=97ccf379-48db-481d-988d-e83e3d76c225; _vwo_uuid_v2=DF926384B38E1A4DDD5B21FE6B65EE1C1|47319990296e61ce77912c327ce867aa; _gid=GA1.2.893003133.1666868935; ExternalReferrer=; BrokerOffice_Visit=0=0ecbd5ae-efca-4d0b-8baa-d79f0a87bed6&1=35009-0-0-False; _ga_XEMPL6HXEJ=GS1.1.1666939492.2.1.1666939547.5.0.0; _ga=GA1.2.903265222.1666868931',
        'referer': 'https://www.longandfoster.com/pages/real-estate-agent-office-search',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_api.format(1), callback=self.parse, headers=self.headers)

    def parse(self, response):
        json_obj = json.loads(response.body)
        if json_obj:
            result = json.loads(json_obj.get('Entity', []))
            for data in result:
                item = dict()
                item['Full Name'] = data.get('DisplayName', '')
                item['First Name'] = data.get('FirstName', '')
                item['Last Name'] = data.get('LastName', '')
                item['Business Name'] = data.get('OfficeName', '')
                item['Street Address'] = data.get('StreetAddress1', '')
                item['State'] = data.get('StateCode', '')
                item['State_Abrv'] = data.get('State', '')
                item['Zip'] = data.get('Zip', '')
                item['Business_Site'] = data.get('OfficeWebsiteURL', '')
                item['Phone Number'] = data.get('Phone', '')
                item['Email'] = data.get('Email', '')
                pid = data.get('PersonID', '')
                detail_url = item['First Name'] + item['Last Name'] + '-' + str(pid)
                item['Detail_Url'] = self.base_url.format(detail_url)
                item['Latitude'] = data.get('Latitude', '')
                item['Longitude'] = data.get('Longitude', '')
                item['Source_URL'] = 'https://longandfoster.com/MD/Washington-Grove'
                item['Occupation'] = 'Realtor'
                item['Lead_Source'] = 'longandfoster'
                item['Record_Type'] = 'Person'
                item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                yield item

        for index in range(2, 42):
            yield scrapy.Request(self.request_api.format(index), callback=self.parse, headers=self.headers)

