from datetime import datetime

import scrapy


class LocationsArbysSpiderSpider(scrapy.Spider):
    name = 'locations_arbys_spider'
    start_urls = ['https://locations.arbys.com/']
    custom_settings = {
        'FEED_URI': 'locations_arbys.csv',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.map-list-item a'):
            state_url = data.css('::attr(href)').get()
            yield response.follow(url=state_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('div.map-list-item a'):
            city_url = data.css('::attr(href)').get()
            yield response.follow(url=city_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('li.map-list-item-wrap'):
            item = dict()
            item['Business Name'] = data.css('a.location-name span::text').get('').strip()
            address = data.css('div.address a::text').get('')
            if address:
                item['Street Address'] = address.split(',')[0].strip()
                state = address.split(',')[-1].strip()
                if len(state.split(' ')) > 1:
                    item['State'] = state.split(' ')[0].strip()
                    item['Zip'] = state.split(' ')[-1].strip()
            item['Phone Number'] = data.css('a.phone::text').get('').strip()
            item['Category'] = data.css('div.pb-20::text').get('').strip()
            item['Source_URL'] = 'https://locations.arbys.com/'
            item['Occupation'] = 'Arbys Store'
            item['Lead_Source'] = 'locations.arbys'
            item['Detail_Url'] = data.css('a.location-name::attr(href)').get('').strip()
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item
