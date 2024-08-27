import scrapy


class DollargeneralSpiderSpider(scrapy.Spider):
    name = 'dollargeneral_spider'
    start_urls = ['https://www.dollargeneral.com/store-directory']

    custom_settings = {
        'FEED_URI': 'dollargeneral.csv',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.state-list-item p a'):
            state_url = data.css('::attr(href)').get()
            yield response.follow(url=state_url, callback=self.get_city_data, headers=self.headers)

    def get_city_data(self, response):
        for data in response.css('div.city-list-item p a'):
            city_url = data.css('::attr(href)').get()
            yield response.follow(url=city_url, callback=self.get_listing, headers=self.headers)

    def get_listing(self, response):
        for data in response.css('div.store-locations-wrapper div.store__card'):
            item = dict()
            item['Phone Number'] = data.css('p.phone::text').get('').strip()
            item['Business Name'] = 'Dollar General Store'
            item['Street Address'] = response.css('p.store__card-title::text').get('').strip()
            detail_url = data.css('a.view-details::attr(href)').get()
            yield response.follow(url=detail_url, meta={'item': item}, callback=self.get_details, headers=self.headers)

    def get_details(self, response):
        item = response.meta['item']
        item['State_Abrv'] = response.css('div.store-details__section div.store-details__main-postal::attr(data-state)').get('').strip()
        item['Zip'] = response.css('div.store-details__section div.store-details__main-postal::attr(data-zip)').get('').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Store'
        item['Source_URL'] = 'https://stores.dollargeneral.com/mo/old-appleton/'
        item['Lead_Source'] = 'dollargeneral'
        yield item
