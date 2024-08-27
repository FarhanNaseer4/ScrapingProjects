import scrapy


class AcremeSpiderSpider(scrapy.Spider):
    name = 'acreme_spider'
    start_urls = ['https://acreme.org.au/regions/']
    base_url = 'https:{}'
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'acreme.csv',
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
        'HTTPERROR_ALLOW_ALL': '200',
    }
    headers = {
        'authority': 'acreme.org.au',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 ',
        'X-Crawlera-Profile': 'pass'
    }

    def parse(self, response):
        for data in response.xpath('//div[@class="l-ahus-main__box"]/h2/following::ul/li[contains(@class,'
                                   '"c-ahus-list__item--4")]/a'):
            comp_cate_url = data.xpath('./@href').get()
            if not comp_cate_url.startswith(self.base_url):
                comp_cate_url = self.base_url.format(comp_cate_url)
            yield scrapy.Request(url=comp_cate_url, callback=self.get_state_url, headers=self.headers)

    def get_state_url(self, response):
        for data in response.css('div.l-ahus-main__box ul.c-ahus-list:nth-child(1) li a'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            yield scrapy.Request(url=state_url, callback=self.get_county_url, headers=self.headers)

    def get_county_url(self, response):
        for data in response.css('div.l-ahus-main__box ul.c-ahus-list:nth-child(1) li a'):
            county_url = data.css('::attr(href)').get()
            if not county_url.startswith(self.base_url):
                county_url = self.base_url.format(county_url)
            yield scrapy.Request(url=county_url, callback=self.get_listing, headers=self.headers)

    def get_listing(self, response):
        for data in response.css('ul.c-ahus-list li div.c-ahus-list__item-main-box'):
            item = dict()
            item['Business Name'] = data.css('a.c-ahus-list__item-name::text').get('').strip()
            item['Detail_Url'] = self.base_url.format(data.css('a.c-ahus-list__item-name::attr(href)').get('').strip())
            item['Occupation'] = data.css('div.c-ahus-list__item-categories a:nth-child(1)::text').get('').strip()
            item['Source_URL'] = 'https://ramsey-indiana.acreme.org.au/professional-services/'
            item['Lead_Source'] = 'ramsey-indiana'
            yield scrapy.Request(url=item['Detail_Url'], meta={'item': item},
                                 callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = response.meta['item']
        item['Full Name'] = response.xpath('//section[@class="l-ahus-article__section"]/p/i[contains(@class,'
                                           '"fa-user")]/following-sibling::text()').get('').strip()
        item['Phone Number'] = response.xpath('//section[@class="l-ahus-article__section"]/p/i[contains(@class,'
                                              '"fa-phone")]/following-sibling::text()').get('').strip()
        street_address = response.xpath('//section[@class="l-ahus-article__section"]/p/i[contains(@class,'
                                        '"fa-map-marker")]/following-sibling::text()').get('').strip()
        if len(street_address.split(',')) > 2:
            item['Street Address'] = street_address.split(',')[0].strip()
            state_address = street_address.split(',')[2].strip()
            if len(state_address.split(' ')) > 1:
                item['State'] = state_address.split(' ')[0].strip()
                item['Zip'] = state_address.split(' ')[1].strip()
        yield item
