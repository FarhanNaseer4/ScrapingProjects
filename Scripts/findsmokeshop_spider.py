import scrapy


class FindsmokeshopSpiderSpider(scrapy.Spider):
    name = 'findsmokeshop_spider'
    start_urls = ['https://findsmokeshop.com/']

    custom_settings = {
        'FEED_URI': 'findsmokeshop.csv',
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
        for data in response.css('div.col-md-4 a'):
            state_url = data.css('::attr(href)').get()
            yield response.follow(url=state_url, callback=self.city_page, headers=self.headers)

    def city_page(self, response):
        for data in response.css('div.col-lg-4 h4 a'):
            city_url = data.css('::attr(href)').get()
            yield response.follow(url=city_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div.col-md-5 h3 a'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('div.col-lg-6 h1::text').get('').strip()
        item['Description'] = response.css('p.lead::text').get('').strip()
        item['Phone Number'] = response.css('div.col-md-6 p a::text').get('').strip()
        item['Street Address'] = response.xpath('//div[@class="col-md-6"]/h4[contains(text(),'
                                                '"Address")]/following-sibling::p/text()').get('').strip()
        address = response.xpath('//div[@class="col-md-6"]/h4[contains(text(),'
                                 '"Address")]/following-sibling::p/br/following-sibling::text()').get('').strip()
        if len(address.split(',')) > 1:
            state = address.split(',')[-1].strip()
            if len(state.split(' ')) > 1:
                item['State_Abrv'] = state.split(' ')[0].strip()
                item['Zip'] = state.split(' ')[1].strip()
        item['Occupation'] = 'Smoke Shop'
        item['Source_URL'] = 'https://findvapeshop.com/kansas/mound-city/mound-city-butcher-block'
        item['Lead_Source'] = 'findvapeshop'
        item['Detail_Url'] = response.url
        yield item

