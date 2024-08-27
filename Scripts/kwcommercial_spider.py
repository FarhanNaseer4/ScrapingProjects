import copy
import json

import scrapy


class KwcommercialSpiderSpider(scrapy.Spider):
    name = 'kwcommercial_spider'
    request_api = 'https://searchv2.realnex.com/api/v2/SearchAgent1'

    custom_settings = {
        'FEED_URI': 'kwcommercial.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
    }

    payload = {"AgentName": "", "AgencyName": "",
               "BrokerTypes": ["investmentsales", "MortgageBroker", "LeasingAgent", "TenantRep", "CorporateService",
                               "Residential"], "LocationData": [], "Market": [], "NoOfRecords": 100, "ListAll": True,
               "ShowMissingMarket": True, "ShowMissingSpeciality": True, "ShowMissingBrokerTypes": True,
               "SortBy": "lastname.raw", "SortHow": "asc",
               "Speciality": ["SCR", "OFC", "IND", "MF", "V", "LH", "SPEC", "HC"], "CompanyIDs": [],
               "OrganizationIDs": [11], "StartIndex": 0}

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json; charset=UTF-8',
        'Origin': 'https://mpdirect.realnex.com',
        'Referer': 'https://mpdirect.realnex.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    def start_requests(self):
        item = {'start': 0}
        yield scrapy.Request(url=self.request_api, method='POST', callback=self.parse, meta={'item': item},
                             body=json.dumps(self.payload), headers=self.headers)

    def parse(self, response):
        start_index = response.meta['item']
        result = json.loads(response.body)
        for data in result[0]:
            item = dict()
            item['Full Name'] = data.get('fullname', '')
            item['First Name'] = data.get('firstname', '')
            item['Last Name'] = data.get('lastname', '')
            item['Email'] = data.get('email', '')
            item['Phone Number'] = data.get('mobilephone', '')
            item['Street Address'] = data.get('userprofile', {}).get('street', '')
            item['State'] = data.get('userprofile', {}).get('state', '')
            item['Zip'] = data.get('userprofile', {}).get('zipcode', '')
            item['Phone Number 1'] = data.get('userprofile', {}).get('businessphone', '')
            item['Latitude'] = data.get('userprofile', {}).get('latitude', '')
            item['Longitude'] = data.get('userprofile', {}).get('longitude', '')
            item['Source_URL'] = 'https://kwcommercial.com/agents/'
            item['Lead_Source'] = 'kwcommercial'
            item['Occupation'] = 'Agent'
            item['Record_Type'] = 'Person'
            yield item

        index = start_index.get('start')
        if index <= 3000:
            index = index + 100
            payload = copy.deepcopy(self.payload)
            payload['StartIndex'] = index
            start_index['start'] = index
            yield scrapy.Request(url=self.request_api, method='POST', callback=self.parse, meta={'item': start_index},
                                 body=json.dumps(payload), headers=self.headers)
