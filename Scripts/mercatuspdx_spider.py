import json

import scrapy


class MercatuspdxSpiderSpider(scrapy.Spider):
    name = 'mercatuspdx_spider'
    request_api = 'https://api.membershipworks.com/v2/directory?_st&_rf=2%20Posted%20on%20directory'
    base_url = 'https://mercatuspdx.com/directory/#!biz/id/{}'
    custom_settings = {
        'FEED_URI': 'mercatuspdx.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
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
        'Connection': 'keep-alive',
        'Origin': 'https://mercatuspdx.com',
        'Referer': 'https://mercatuspdx.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'X-Org': '14363',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_api, callback=self.parse, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.body)
        for data in result.get('usr', []):
            item = dict()
            item['Business Name'] = data.get('nam', '')
            item['Business_Site'] = data.get('web', '')
            u_id = data.get('uid', '')
            if u_id:
                item['Detail_Url'] = self.base_url.format(u_id)
            phone = data.get('phn', [])
            if phone:
                item['Phone Number'] = phone[0]
            else:
                item['Phone Number'] = ''
            location = data.get('loc', [])
            if location:
                item['Latitude'] = location[0]
                item['Longitude'] = location[1]
            else:
                item['Latitude'] = ''
                item['Longitude'] = ''
            item['Occupation'] = 'Business Service'
            item['Source_URL'] = 'https://mercatuspdx.com/directory/black-owned-businesses/'
            item['Lead_Source'] = 'mercatuspdx'
            yield item
