import scrapy


class AvvoSpiderSpider(scrapy.Spider):
    name = 'avvo_spider'
    start_urls = ['https://www.avvo.com/find-a-lawyer/all-practice-areas']
    base_url = 'https://www.avvo.com{}'
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'HTTPERROR_ALLOW_ALL': True,
        'FEED_URI': 'avvo_lawyers.csv',
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
        for data in response.css('div.v-content-wrapper h4 a'):
            practice_url = data.css('::attr(href)').get()
            if not practice_url.startswith(self.base_url):
                practice_url = self.base_url.format(practice_url)
            yield scrapy.Request(url=practice_url, callback=self.parse_state, headers=self.headers)

    def parse_state(self, response):
        for data in response.css('div[id="js-top-state-link-farm"] ol li a'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            yield scrapy.Request(url=state_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.lawyer-info-container a.search-result-lawyer-name'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, headers=self.headers)

        next_page = response.css('li.pagination-next a::attr(href)').get('').strip()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse_listing,
                                 headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        fullname = response.css('h1.u-vertical-margin-0 span[itemprop="name"]::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['State_Abrv'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Phone Number'] = response.css('span[itemprop="telephone"] a span::text').get('').strip()
        item['Source_URL'] = 'https://www.avvo.com/find-a-lawyer/all-practice-areas'
        item['Lead_Source'] = 'avvo'
        item['Occupation'] = 'Attorney'
        item['Detail_Url'] = response.url
        yield item

