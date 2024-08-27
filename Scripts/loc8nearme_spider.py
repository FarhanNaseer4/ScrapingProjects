import scrapy


class Loc8nearmeSpiderSpider(scrapy.Spider):
    name = 'loc8nearme_spider'
    start_urls = ['http://loc8nearme.com/']
    custom_settings = {
        'FEED_URI': 'loc8nearme.csv',
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
        'authority': 'www.loc8nearme.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('ul.bullets a'):
            city_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=city_url, callback=self.business_listing, headers=self.headers)

    def business_listing(self, response):
        for data in response.css('div.grid div.wrapper'):
            check_state = data.css('small::text').get('')
            if 'locations' in check_state:
                listing_url = data.css('h3 a::attr(href)').get()
                yield response.follow(url=listing_url, callback=self.listing_page, headers=self.headers)
            else:
                item = dict()
                item['Business Name'] = data.css('h3 a::text').get('').strip()
                detail_url = data.css('h3 a::attr(href)').get()
                yield response.follow(url=detail_url, meta={'item': item}, callback=self.detail_page,
                                      headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div.wrap_bread_info h2 a'):
            item = dict()
            item['Business Name'] = data.css('::text').get('').strip()
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, meta={'item': item}, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = response.meta['item']
        item['Detail_Url'] = response.url
        item['Business_Type'] = response.css('div.content-article h1::text').get('').strip()
        item['Rating'] = response.css('span.rating-span span::text').get('').strip()
        item['Phone Number'] = response.css('a[id="phone"]::attr(href)').get('').replace('tel:', '').strip()
        address = response.css('span[id="fullAddress"]::text').get('').strip()
        if len(address.split(',')) > 1:
            item['Street Address'] = address.split(',')[0].strip()
            state = address.split(',')[-1].strip()
            if len(state.split(' ')) > 1:
                item['Zip'] = state.split(' ')[-1].strip()
        item['Occupation'] = 'Business Service'
        item['Source_URL'] = 'https://www.loc8nearme.com/'
        item['Lead_Source'] = 'loc8nearme'
        yield item
