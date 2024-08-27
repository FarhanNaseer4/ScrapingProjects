import scrapy


class EzlocalSpiderSpider(scrapy.Spider):
    name = 'ezlocal_spider'
    start_urls = ['https://ezlocal.com/']
    base_url = 'https://ezlocal.com/{}'
    headers = {
        'authority': 'ezlocal.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'HTTPERROR_ALLOW_ALL': True,
        'FEED_URI': 'ezlocal.csv',
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

    def parse(self, response):
        for data in response.css('div[id="states"] a'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            yield scrapy.Request(url=state_url, callback=self.city_page, headers=self.headers)

    def city_page(self, response):
        for data in response.xpath(
                '//div[@class="col-sm-12"]/h2[contains(text(), " Cities")]/following-sibling::ul//a'):
            city_url = data.xpath('./@href').get()
            if not city_url.startswith(self.base_url):
                city_url = self.base_url.format(city_url)
            yield scrapy.Request(url=city_url, callback=self.category_page, headers=self.headers)

    def category_page(self, response):
        for data in response.xpath('//div[@class="col-sm-4"]/h4/following-sibling::ul/li/a'):
            listing_url = data.xpath('./@href').get()
            if not listing_url.startswith(self.base_url):
                listing_url = self.base_url.format(listing_url)
            yield scrapy.Request(url=listing_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div.vcard h3.org a'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('span[itemprop="name"]::text').get('').strip()
        item['Street Address'] = response.css('div[itemprop="streetAddress"]::text').get('').strip()
        item['State_Abrv'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Phone Number'] = response.css('div[itemprop="telephone"]::text').get('').strip()
        item['Occupation'] = response.css('div.category a::text').get('').strip()
        item['Business_Site'] = response.css('div.website a::attr(href)').get('').strip()
        item['Email'] = response.css('div.pemail::text').get('').strip()
        item['Description'] = response.xpath('//div[@class="pdescription"]/text()').get('').strip()
        item['Source_URL'] = 'https://ezlocal.com/'
        item['Lead_Source'] = 'ezlocal'
        yield item
