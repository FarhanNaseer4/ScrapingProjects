import re
from datetime import datetime

import scrapy


class BarnesvilleSpider(scrapy.Spider):
    name = 'barnesville'
    start_urls = ['https://barnesville.org/list']

    custom_settings = {
        'FEED_URI': 'barnesville.csv',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div[id="mn-alphanumeric"] a'):
            url = data.css('::attr(href)').get()
            item = dict()
            item['Meta_Description'] = response.xpath('//meta[@name="description" or '
                                                      '@property="og:description"]/@content').get('').strip()
            if url:
                yield response.follow(url=url, callback=self.parse_listing, headers=self.headers, meta={'item': item})

    def parse_listing(self, response):
        item = response.meta['item']
        for data in response.css('div[itemprop="name"] a'):
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.detail_page, headers=self.headers,
                                      meta={'item': item})

    def detail_page(self, response):
        try:
            item = response.meta['item']
            item['Business Name'] = response.css('div.cm_ml02_member_name::text').get('').strip()
            contact_detail = ', '.join(response.xpath('//div[@class="cm_ml02_sreet_address"]/text()').getall())
            try:
                states = re.findall(r'\b[A-Z]{2}\b', contact_detail)
                if len(states) == 2:
                    state = states[-1]
                else:
                    state = states[0]
            except:
                state = ''
            try:
                street = contact_detail.rsplit(state, 1)[0].strip().rstrip(',').strip()
            except:
                street = ''
            try:
                zip_code = re.search(r"(?!\A)\b\d{5}(?:-\d{4})?\b", contact_detail).group(0)
            except:
                zip_code = ''
            item['Street Address'] = street
            item['State'] = state
            item['Zip'] = zip_code
            item['Phone Number'] = response.css('div.cm_ml02_phone::text').get('').strip()
            item['Business_Site'] = response.css('div.cm_ml02_website_address a::attr(href)').get('').strip()
            item['Source_URL'] = 'https://barnesville.org/list'
            item['Occupation'] = response.css('div.cm_ml02_member_categories::text').get('').strip()
            item['Lead_Source'] = 'barnesville'
            item['Detail_Url'] = response.url
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item
        except:
            print('Error')
