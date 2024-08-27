import scrapy


class CmacSpiderSpider(scrapy.Spider):
    name = 'cmac_spider'
    start_urls = ['https://www.cmac.ws/categories/']
    custom_settings = {
        'FEED_URI': 'cmac_categories.csv',
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
        'authority': 'www.cmac.ws',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('ul.card-columns li a'):
            url = data.css('::attr(href)').get()
            yield scrapy.Request(url=url, callback=self.get_state_url, headers=self.headers)

    def get_state_url(self, response):
        for data in response.css('ul.card-columns li a'):
            url = data.css('::attr(href)').get()
            yield scrapy.Request(url=url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.col-md-8 h3 a'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_listing, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('section[id="description"] h1::text').get('').strip()
        item['Street Address'] = response.xpath('//section[@id="description"]/h2/text()').get('').strip()
        state_add = response.xpath('//section[@id="description"]/h2/span/following::text()').get('').strip()
        if len(state_add.split(',')) > 2:
            item['State'] = state_add.split(',')[0].strip()
            item['State_Abrv'] = state_add.split(',')[1].strip()
            item['Zip'] = state_add.split(',')[2].strip()
        item['Phone Number'] = response.css('h3 a::text').get('').strip()
        item['Occupation'] = response.css('section[id="description"] p a::text').get('').strip()
        item['Source_URL'] = 'https://paint-stores.cmac.ws/sherwin-williams/12346/'
        item['Lead_Source'] = 'paint-stores'
        yield item

