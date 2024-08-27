import scrapy


class NoloSpiderSpider(scrapy.Spider):
    name = 'nolo_spider'
    start_urls = ['https://www.nolo.com/lawyers']
    base_url = 'https://www.nolo.com{}'
    zyte_key = '025859a924e849f8a528b81142aaae88'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'nolo.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation'],
        'HTTPERROR_ALLOW_ALL': True,
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
        for data in response.css('ul.aop-or-state-list li a'):
            pract_url = data.css('::attr(href)').get()
            if not pract_url.startswith(self.base_url):
                pract_url = self.base_url.format(pract_url)
            yield scrapy.Request(url=pract_url, callback=self.state_page, headers=self.headers)

    def state_page(self, response):
        for data in response.css('ul.aop-or-state-list li a'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            yield scrapy.Request(url=state_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div.profile-info h4 a'):
            list_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=list_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('div.name-tagline-badge-container h1::text').get('').strip()
        item['Street Address'] = response.xpath('//div[contains(text(),"Main '
                                                'Office")]/following-sibling::p/br/following-sibling::text()').get(
            '').strip()
        item['Phone Number'] = response.xpath('//div[contains(text(),"Phone")]/following-sibling::p/text()').get('').strip()
        item['Business_Site'] = response.css('p.subsection-paragraph a::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://www.nolo.com/lawyers'
        item['Lead_Source'] = 'nolo'
        item['Occupation'] = 'Lawyers'
        yield item

