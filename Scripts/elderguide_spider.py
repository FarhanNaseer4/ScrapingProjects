import scrapy


class ElderguideSpiderSpider(scrapy.Spider):
    name = 'elderguide_spider'
    start_urls = ['https://elderguide.com/nursing-homes/']
    base_url = 'https://elderguide.com{}'

    custom_settings = {
        'FEED_URI': 'elderguide.csv',
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

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('span.p-4 a.underline'):
            state_url = data.css('::attr(href)').get()
            yield response.follow(url=state_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('span.p-4 a.underline'):
            city_url = data.css('::attr(href)').get()
            yield response.follow(url=city_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.grid-cols-1fr article'):
            item = dict()
            item['Business Name'] = data.css('h3 a::text').get('').strip()
            detail_url = data.css('h3 a::attr(href)').get()
            item['Street Address'] = data.xpath('.//p/span[contains(@class,"sr-only")]/following-sibling::text()').get('').strip()
            state = data.xpath('.//p/span[contains(@class,"sr-only")]/following-sibling::br/following-sibling::text()').get('').strip()
            if state:
                if len(state.split(',')) > 1:
                    state_abb = state.split(',')[-1].strip()
                    if len(state_abb.split(' ')) > 1:
                        item['State'] = state_abb.split(' ')[0].strip()
                        item['Zip'] = state_abb.split(' ')[-1].strip()
            item['Phone Number'] = data.css('div.pt-4 a::attr(href)').get('').replace('tel:', '').strip()
            if detail_url:
                yield response.follow(url=detail_url,callback=self.parse_detail,
                                      meta={'item': item}, headers=self.headers)
            else:
                item['Occupation'] = 'Nursing Home'
                item['Source_URL'] = 'https://elderguide.com/nursing-homes/'
                item['Lead_Source'] = 'elderguide'
                yield item

    def parse_detail(self, response):
        item = response.meta['item']
        item['Detail_Url'] = response.url
        item['Business_Site'] = response.css('section.px-4 a.w-fit::attr(href)').get('').strip()
        item['Description'] = response.css('section.px-4 div.article-content p::text').get('').strip()
        item['Occupation'] = 'Nursing Home'
        item['Source_URL'] = 'https://elderguide.com/nursing-homes/'
        item['Lead_Source'] = 'elderguide'
        yield item


