import scrapy


class EcondolenceSpiderSpider(scrapy.Spider):
    name = 'econdolence_spider'
    start_urls = ['https://www.econdolence.com/trusted-business-directory-landing-page/']
    base_url = 'https://www.econdolence.com/{}'
    custom_settings = {
        'FEED_URI': 'econdolence.csv',
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('ul.state a.stateName'):
            state_url = data.css('::attr(href)').get()
            if state_url:
                if not state_url.startswith(self.base_url):
                    state_url = self.base_url.format(state_url)
                yield scrapy.Request(url=state_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('ul.city a'):
            city_url = data.css('::attr(href)').get()
            if city_url:
                if not city_url.startswith(self.base_url):
                    city_url = self.base_url.format(city_url)
                yield scrapy.Request(url=city_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.card h3 a'):
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('div.row h1::text').get('').strip()
        address = response.css('span[id="Cnt_Body_Cnt_Content_element_14589_AddressField"]::text').get('').strip()
        if address:
            item['Street Address'] = address.split(',')[0].strip()
            item['Zip'] = address.split(',')[-1].strip()
        item['Phone Number'] = response.css('a[id="Cnt_Body_Cnt_Content_element_14589_PhoneNavigation"]::text').get('').strip()
        item['Business_Site'] = response.css('a[id="Cnt_Body_Cnt_Content_element_14589_WebsiteNavigation"]::attr(href)').get('').strip()
        item['Description'] = response.css('div.descriptionWrapper div::text').get('').strip()
        item['Source_URL'] = 'https://www.econdolence.com/trusted-business-directory-landing-page/'
        item['Lead_Source'] = 'econdolence'
        item['Occupation'] = 'Trusted Business'
        item['Detail_Url'] = response.url
        yield item
