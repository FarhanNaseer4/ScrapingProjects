from datetime import datetime

import scrapy


class HomecontractorsSpiderSpider(scrapy.Spider):
    name = 'homecontractors_spider'
    start_urls = ['https://www.hometowndemolitioncontractors.com/']

    custom_settings = {
        'FEED_URI': 'hometowndemolitioncontractors.csv',
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('ul.all-states li a'):
            state_url = data.css('::attr(href)').get()
            yield response.follow(url=state_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('ul.all-cities li a'):
            city_url = data.css('::attr(href)').get()
            yield response.follow(url=city_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.flex-head'):
            item = dict()
            item['Business Name'] = data.css('h2 span::text').get('').strip()
            item['Phone Number'] = data.css('span[itemprop="telephone"]::text').get('').strip()
            address = data.css('span[itemprop="address"]::text').get('').strip()
            if address:
                item['Street Address'] = address.split(',')[0].strip()
                state = address.split(',')[-1].strip()
                if len(state.split(' ')) > 1:
                    item['State'] = state.split(' ')[1].strip()
                    item['Zip'] = state.split(' ')[-1].strip()
            item['Meta_Description'] = response.xpath('//meta[@name="description" or '
                                                      '@property="og:description"]/@content').get('').strip()
            detail_url = data.css('h2 a::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail,
                                      headers=self.headers, meta={'item': item})
            else:
                item['Source_URL'] = 'https://www.hometowndemolitioncontractors.com/'
                item['Lead_Source'] = 'hometowndemolitioncontractors'
                item['Occupation'] = 'Demolition Contractor'
                item['Record_Type'] = 'Business'
                item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                yield item

    def parse_detail(self, response):
        item = response.meta['item']
        item['Services'] = ', '.join(data.css('::text').get('') for data in response.css('ul.service_links li a'))
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://www.hometowndemolitioncontractors.com/'
        item['Lead_Source'] = 'hometowndemolitioncontractors'
        item['Occupation'] = 'Demolition Contractor'
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item
