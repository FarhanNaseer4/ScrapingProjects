import csv

import scrapy


class NbccSpiderSpider(scrapy.Spider):
    name = 'nbcc_spider'
    request_api = 'https://nbcc.org/search/acep_by_state?statecode={}'

    custom_settings = {
        'FEED_URI': 'greenamerica.csv',
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

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_key = self.get_search_urls()

    def get_search_urls(self):
        with open('states.csv', 'r', encoding='utf-8-sig') as reader:
            return list(csv.DictReader(reader))

    def start_requests(self):
        for data in self.request_key:
            yield scrapy.Request(url=self.request_api.format(data.get('States')), callback=self.parse,
                                 headers=self.headers)

    def parse(self, response):
        for data in response.css('table[id="Notes"] tr td:nth-child(6)'):
            item = dict()
            item['Business Name'] = data.xpath('.//li/strong[contains(text(), "Provider:")]/following-sibling::text()').get('').strip()
            item['Phone Number'] = data.xpath('.//li/strong[contains(text(), "Phone:")]/following-sibling::text()').get('').strip()
            item['Email'] = data.css('li a::text').get('').strip()
            item['Street Address'] = data.xpath('.//li/strong[contains(text(), "Address:")]/following-sibling::text()').get('').strip()
            fullname = data.xpath('.//li/strong[contains(text(), "ContactName:")]/following-sibling::text()').get('').strip()
            if fullname:
                item['Full Name'] = fullname
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = fullname.split(' ')[-1].strip()
            item['Source_URL'] = 'https://nbcc.org/search/acep_by_state?statecode=AL'
            item['Occupation'] = 'Business Service'
            item['Lead_Source'] = 'nbcc.org'
            item['Record_Type'] = 'Business'
            yield item
