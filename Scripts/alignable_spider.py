import scrapy


class AlignableSpiderSpider(scrapy.Spider):
    name = 'alignable_spider'
    start_urls = ['https://www.alignable.com/alvin-tx/directory']
    base_url = 'https://www.alignable.com{}'
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'alignable.csv',
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
        'authority': 'www.alignable.com',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 ',
        'X-Crawlera_Profile': 'pass'
    }

    def parse(self, response):
        for data in response.css('div.overflow-hidden'):
            url = data.css('.relative a.text-main-text::attr(href)').get()
            if not url.startswith(self.base_url):
                url = self.base_url.format(url)
            yield scrapy.Request(url=url, callback=self.parse_data, headers=self.headers)

        next_page = response.css('div.infinite-scroll-next-page::attr(data-infinite-scroll-url)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)

    def parse_data(self, response):
        item = dict()
        item['Business Name'] = response.css('div.business-profile-banner__text-line1 h1::text').get('').strip()
        address = response.css('div.profile-info li.profile-info__line div:nth-child(2) a::text').get('').strip()
        if len(address.split(',')) > 1:
            item['Street Address'] = address.split(',')[0]
            state = address.split(',')[1].strip()
            if len(state.split(' ')) > 1:
                item['State_Abrv'] = state.split(' ')[0].strip()
                item['Zip'] = state.split(' ')[1].strip()
        item['Phone Number'] = response.xpath('//div[@class="profile-info"]/*//a[contains(@href,"tel:")]/text()').get('').strip()
        item['Business_Site'] = response.xpath('//div[@class="profile-info"]/*//a[@target="_blank"]/@href').get('').strip()
        item['Description'] = response.css('div.profile-text--large p::text').get('').strip()
        item['Source_URL'] = 'https://alignable.com/alvin-tx/directory'
        item['Lead_Source'] = 'alignable'
        item['Occupation'] = 'Contractor'
        yield item


