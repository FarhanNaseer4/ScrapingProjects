import scrapy


class LowesSpiderSpider(scrapy.Spider):
    name = 'lowes_spider'
    start_urls = ['https://www.lowes.com/Lowes-Stores']
    base_url = 'https://www.lowes.com{}'
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'lowes_stores.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'HTTPERROR_ALLOW_ALL': True,
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
        'authority': 'www.lowes.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.jsyiyD a'):
            city_url = data.css('::attr(href)').get()
            if not city_url.startswith(self.base_url):
                city_url = self.base_url.format(city_url)
            yield scrapy.Request(url=city_url, callback=self.get_store_url, headers=self.headers)

    def get_store_url(self, response):
        for data in response.css('div.city-name a'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('h1[id="storeHeader"]::text').get('').strip()
        item['Phone Number'] = response.css('span[data-id="sc-main-phone"]::text').get('').strip()
        item['Phone Number 1'] = response.css('span[data-id="sc-pro-phone"]::text').get('').strip()
        item['Street Address'] = response.css('div.location div:nth-child(1)::text').get('').strip()
        state_detail = response.css('div.location div:nth-child(2)::text').get('').strip()
        if len(state_detail.split(',')) > 1:
            state_abb = state_detail.split(',')[1].strip()
            if len(state_abb.split(' ')) > 1:
                item['State_Abrv'] = state_abb.split(' ')[0].strip()
                item['Zip'] = state_abb.split(' ')[1].strip()
        item['Description'] = response.css('div.store-description p::text').get('').strip()
        item['Source_URL'] = 'https://www.lowes.com/Lowes-Stores'
        item['Lead_Source'] = 'lowes'
        item['Occupation'] = 'Lowes Store'
        yield item



