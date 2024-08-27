import json

import scrapy


class JustiaSpiderSpider(scrapy.Spider):
    name = 'justia_spider'
    base_url = 'https://www.justia.com{}'
    request_url = 'https://www.justia.com/lawyers/new-york/valley-stream'
    custom_settings = {
        'FEED_URI': 'justia.csv',
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
        'authority': 'www.justia.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_url, callback=self.parse, headers=self.headers)

    def parse(self, response):
        json_obj = response.css('script[type="application/javascript"]::text').re_first('window.profiles = (.+);')
        result = json.loads(json_obj)
        for data in result:
            url = result.get(data, {}).get('link', '')
            if not url.startswith(self.base_url):
                url = self.base_url.format(url)
            yield scrapy.Request(url=url, callback=self.parse_data, headers=self.headers)

        next_page = response.css('span.next a::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse, headers=self.headers)

    def parse_data(self, response):
        item = dict()
        item['Full Name'] = response.css('h1.lawyer-name::text').get('').strip()
        item['Business Name'] = response.css('div.has-no-bottom-padding span.small-font::text').get('').strip()
        item['Phone Number'] = response.css('div.reset-width-below-tablet span.value span::text').get('').strip()
        item['State_Abrv'] = response.css('div.reset-width-below-tablet span.region::text').get('').strip()
        item['Zip'] = response.css('div.reset-width-below-tablet span.postal-code::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Lawyer'
        item['Source_URL'] = 'https://law.justia.com/constitution/us/ordinances-held-unconstitutional.html'
        item['Lead_Source'] = 'law.justia'
        yield item
