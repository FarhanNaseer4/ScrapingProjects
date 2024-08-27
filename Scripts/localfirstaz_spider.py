import json

import scrapy


class LocalfirstazSpiderSpider(scrapy.Spider):
    name = 'localfirstaz_spider'
    request_api = 'https://api.membershipworks.com/v2/directory?_st&_rf=Members'
    detail_page = 'https://api.membershipworks.com/v2/account/{}/profile'
    custom_settings = {
        'FEED_URI': 'localfirstaz.csv',
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
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Origin': 'https://localfirstaz.com',
        'Referer': 'https://localfirstaz.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
        'X-Org': '25054',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_api, callback=self.parse, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.body)
        for data in result.get('usr', []):
            uid = data.get('uid', '')
            yield scrapy.Request(url=self.detail_page.format(uid), callback=self.parse_data, headers=self.headers)

    def parse_data(self, response):
        result = json.loads(response.body)
        item = dict()
        item['Business Name'] = result.get('nam', '')
        item['Street Address'] = result.get('adr', {}).get('ad1', '')
        item['State_Abrv'] = result.get('adr', {}).get('sta', '')
        item['Zip'] = result.get('adr', {}).get('zip', '')
        item['Phone Number'] = result.get('phn', '')
        item['Email'] = result.get('eml', '')
        item['Business_Site'] = result.get('web', '')
        item['Source_URL'] = 'https://localfirstaz.com/directory'
        item['Lead_Source'] = 'localfirstaz'
        item['Occupation'] = 'Services'
        yield item


