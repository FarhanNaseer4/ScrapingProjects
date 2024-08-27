import scrapy


class FlowershopfloristsSpiderSpider(scrapy.Spider):
    name = 'flowershopflorists_spider'
    start_urls = ['https://www.flowershopflorists.com/']
    custom_settings = {
        'FEED_URI': 'flowershopflorists.csv',
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
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    }

    def parse(self, response):
        for data in response.css('.small-4 li a'):
            state = data.css('::attr(href)').get()
            yield scrapy.Request(url=state, callback=self.get_city_url, headers=self.headers)

    def get_city_url(self, response):
        for data in response.css('div.small-6 li a'):
            city_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=city_url, callback=self.parse_listing, headers=self.headers, dont_filter=True)

    def parse_listing(self, response):
        for data in response.css('div.fl-info h3 a'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers, dont_filter=True)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('table.unstriped tr:nth-child(1) td:nth-child(2)::text').get('').strip()
        item['Street Address'] = response.css('table.unstriped tr:nth-child(2) td:nth-child(2)::text').get('').strip()
        item['State'] = response.css('table.unstriped tr:nth-child(4) td:nth-child(2)::text').get('').strip()
        item['Phone Number'] = response.css('table.unstriped tr:nth-child(5) td:nth-child(2)::text').get('').strip()
        item['Zip'] = response.css('table.unstriped tr:nth-child(6) td:nth-child(2)::text').get('').strip()
        item['Latitude'] = response.css('table.unstriped tr:nth-child(7) td:nth-child(2)::text').get('').strip()
        item['Longitude'] = response.css('table.unstriped tr:nth-child(8) td:nth-child(2)::text').get('').strip()
        item['Business_Site'] = response.css('table.unstriped tr:nth-child(9) td:nth-child(2)::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Florists'
        item['Source_URL'] = 'https://www.flowershopflorists.com/'
        item['Lead_Source'] = 'flowershopflorists'
        yield item
