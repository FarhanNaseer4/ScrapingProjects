import json
from datetime import datetime

import scrapy


class CrmcSpiderSpider(scrapy.Spider):
    name = 'crmc_spider'
    request_api = 'https://www.crmc.org/api/pd/getProviders?containerId=1402'
    base_url = 'https://www.crmc.org{}'
    custom_settings = {
        'FEED_URI': 'crmc.csv',
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
        'authority': 'www.crmc.org',
        'accept': 'application/json',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': '_gid=GA1.2.100022772.1667203882; _gcl_au=1.1.644936935.1667203883; ASP.NET_SessionId=hqj5b33x3k04lvpiiqb0vytq; _ga_90LLWGHTVP=GS1.1.1667284300.2.1.1667284503.0.0.0; _ga=GA1.2.838969163.1667203878; _gat=1; _gat_client=1',
        'referer': 'https://www.crmc.org/provider-directory/',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_api, callback=self.parse, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.body)
        for data in result:
            item = dict()
            item['Full Name'] = data.get('name', '')
            item['First Name'] = data.get('firstName', '')
            item['Last Name'] = data.get('lastName', '')
            detail_url = data.get('url', '')
            if detail_url:
                item['Detail_Url'] = self.base_url.format(detail_url)
            add = data.get('addresses', [])
            if add:
                address = add[0]
                item['Business Name'] = address.get('officeTitle', '')
                item['Phone Number'] = address.get('phone', '')
                item['Phone Number 1'] = address.get('phone2', '')
                item['Street Address'] = address.get('address1', '')
                item['State'] = address.get('state', '')
                item['Zip'] = address.get('zipCode', '')
                item['Latitude'] = address.get('latitude', '')
                item['Longitude'] = address.get('longitude', '')
            item['Source_URL'] = 'https://www.crmc.org/provider-directory/'
            item['Meta_Description'] = 'View current providers at Capital Region Medical Center.'
            item['Occupation'] = 'Health Care Provider'
            item['Lead_Source'] = 'crmc'
            item['Record_Type'] = 'Person'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item
