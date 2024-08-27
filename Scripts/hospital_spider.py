import scrapy


class HospitalSpiderSpider(scrapy.Spider):
    name = 'hospital_spider'
    start_urls = ['https://www.healthcare4ppl.com/hospital']
    base_url = 'https://www.healthcare4ppl.com{}'
    # custom_settings = {
    #     'FEED_URI': 'healthcare_Hospital.csv',
    #     'FEED_FORMAT': 'csv',
    #     'FEED_EXPORT_ENCODING': 'utf-8-sig',
    #     'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
    #                            'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
    #                            'Business_Site', 'Social_Media',
    #                            'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
    #                            'Latitude', 'Longitude', 'Occupation',
    #                            'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
    #                            'SIC_Sectors', 'SIC_Categories',
    #                            'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
    # }
    headers = {
        'authority': 'www.healthcare4ppl.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('li.state-item a'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            yield scrapy.Request(url=state_url, callback=self.get_city_url, headers=self.headers)

    def get_city_url(self, response):
        for data in response.css('li.city-item a'):
            city_url = data.css('::attr(href)').get()
            if not city_url.startswith(self.base_url):
                city_url = self.base_url.format(city_url)
            yield scrapy.Request(url=city_url, callback=self.get_listing_page, headers=self.headers)

    def get_listing_page(self, response):
        for data in response.css('ol.subject-list div.h4 a'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.get_detail_page, headers=self.headers)

    def get_detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('div.col-md-9 h1::text').get('').strip()
        item['Phone Number'] = response.css('div.phone a.phone::text').get('').strip()
        street_address = response.css('span.marker-locator::text').get('').strip()
        if len(street_address.split(',')) >= 3:
            item['Street Address'] = street_address.split(',')[0].strip()
            state_data = street_address.split(',')[-1].strip()
            if len(state_data.split(' ')) > 1:
                item['State_Abrv'] = state_data.split(' ')[0].strip()
                item['Zip'] = state_data.split(' ')[1].strip()
        else:
            if len(street_address.split(',')) <= 2:
                item['Street Address'] = street_address.split(',')[0].strip()
                state_data = street_address.split(',')[2].strip()
                if len(state_data.split(' ')) > 1:
                    item['State_Abrv'] = state_data.split(' ')[0].strip()
                    item['Zip'] = state_data.split(' ')[1].strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('span.hidden-xs a'))
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Hospital'
        item['Source_URL'] = 'https://www.healthcare4ppl.com/hospital'
        item['Lead_Source'] = 'healthcare4ppl'
        yield item
