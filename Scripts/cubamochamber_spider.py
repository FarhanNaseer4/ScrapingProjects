import json
from datetime import datetime

import scrapy


class CubamochamberSpiderSpider(scrapy.Spider):
    name = 'cubamochamber_spider'
    request_id = 'https://api.membershipworks.com/v2/directory?_st&_rf=Members'
    detail_api = 'https://api.membershipworks.com/v2/account/{}/profile'
    base_url = 'https://cubamochamber.com/chamber-business-directory/#!biz/id/{}'
    custom_settings = {
        'FEED_URI': 'cubamochamber.csv',
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
        'Accept': 'application/json',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'X-Org': '28825',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_id, callback=self.parse, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.body)
        for data in result.get('usr', []):
            u_id = data.get('uid', '')
            yield scrapy.Request(url=self.detail_api.format(u_id), callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        result = json.loads(response.body)
        item = dict()
        item['Business Name'] = result.get('nam', '')
        fullname = result.get('ctc', '')
        if fullname:
            item['Full Name'] = fullname.strip()
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Phone Number'] = result.get('phn', '')
        uid = result.get('uid', '')
        if uid:
            item['Detail_Url'] = self.base_url.format(uid)
        item['Street Address'] = result.get('adr', {}).get('ad1', '')
        item['State'] = result.get('adr', {}).get('sta', '')
        item['Zip'] = result.get('adr', {}).get('zip', '')
        item['Business_Site'] = result.get('web', '')
        item['Source_URL'] = 'https://cubamochamber.com/chamber-business-directory/#!directory'
        item['Meta_Description'] = 'BUSINESS DIRECTORY Loading'
        item['Occupation'] = 'Business Service'
        item['Lead_Source'] = 'cubamochamber'
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item

