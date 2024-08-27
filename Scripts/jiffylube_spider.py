import json

import scrapy


class JiffylubeSpiderSpider(scrapy.Spider):
    name = 'jiffylube_spider'
    start_urls = ['https://www.jiffylube.com/locations/location-directory']
    base_url = 'https://www.jiffylube.com/locations/{}'
    detail_base = 'https://www.jiffylube.com{}'

    custom_settings = {
        'FEED_URI': 'jiffylube.csv',
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
        'authority': 'www.jiffylube.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('li.state a'):
            url = data.css('::attr(href)').get()
            if not url.startswith(self.base_url):
                url = self.base_url.format(url)
            yield scrapy.Request(url=url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        json_obj = response.css('script[type="application/json"]::text').get()
        result = json.loads(json_obj)
        city_data = result.get('props', {}).get('pageProps', {}).get('cities', [])
        for city in city_data:
            location = city.get('locations', [])
            for data in location:
                item = dict()
                item['Business Name'] = data.get('nickname', '')
                item['Street Address'] = data.get('address', '')
                item['State_Abrv'] = data.get('state', '')
                item['Zip'] = data.get('postal_code', '')
                item['Detail_Url'] = self.base_url.format(data.get('_links', {}).get('_self', ''))
                item['Phone Number'] = data.get('phone_main', '')
                item['Occupation'] = data.get('site_type', '')
                item['Latitude'] = data.get('coordinates', {}).get('latitude', '')
                item['Longitude'] = data.get('coordinates', {}).get('longitude', '')
                item['Source_URL'] = 'https://jiffylube.com/locations/il/hanover-park/1835'
                item['Lead_Source'] = 'jiffylube'
                yield item
