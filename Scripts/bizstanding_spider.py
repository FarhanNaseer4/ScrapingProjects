import scrapy


class BizstandingSpiderSpider(scrapy.Spider):
    name = 'bizstanding_spider'
    start_urls = ['https://bizstanding.com/directory/KS/']
    base_url = 'https://bizstanding.com{}'
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'bizstandings.csv',
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
        'authority': 'bizstanding.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.col-sm-8 a.b-letter-nav_link'):
            comp_url = data.css('::attr(href)').get()
            if not comp_url.startswith(self.base_url):
                comp_url = self.base_url.format(comp_url)
            yield scrapy.Request(url=comp_url, callback=self.get_company_data, headers=self.headers)

    def get_company_data(self, response):
        for data in response.css('div.b-letter-nav a'):
            listing_url = data.css('::attr(href)').get()
            if not listing_url.startswith(self.base_url):
                listing_url = self.base_url.format(listing_url)
            yield scrapy.Request(url=listing_url, callback=self.get_listing, headers=self.headers)

    def get_listing(self, response):
        if response.css('div.b-letter-nav a::attr(href)').get():
            for data in response.css('div.b-letter-nav a'):
                new_url = data.css('::attr(href)').get()
                if not new_url.startswith(self.base_url):
                    new_url = self.base_url.format(new_url)
                    yield scrapy.Request(url=new_url, callback=self.get_company_data, headers=self.headers)
        else:
            for data in response.css('div.b-business-item'):
                item = dict()
                item['Business Name'] = data.css('font[itemprop="name"]::text').get('').strip()
                item['Phone Number'] = data.css('span[itemprop="telephone"]::text').get('').strip()
                item['Full Name'] = data.css('span.pfl-member-wrap::text').get('').strip()
                item['Street Address'] = data.css('span[itemprop="streetAddress"]::text').get('').strip()
                item['State'] = data.css('span[itemprop="addressLocality"]::text').get('').strip()
                item['State_Abrv'] = data.css('span[itemprop="addressRegion"]::text').get('').strip()
                item['Zip'] = data.css('span[itemprop="postalCode"]::text').get('').strip()
                detail_url = data.css('a[itemprop="url"]::attr(href)').get()
                if detail_url:
                    item['Detail_Url'] = self.base_url.format(detail_url)
                item['Occupation'] = 'Business Services'
                item['Source_URL'] = 'https://www.brightlocal.com/agency-directory/#'
                item['Lead_Source'] = 'bizstanding'
                yield item






