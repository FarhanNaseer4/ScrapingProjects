import scrapy


class CaringSpiderSpider(scrapy.Spider):
    name = 'caring_spider'
    start_urls = ['https://www.caring.com/senior-care/']
    custom_settings = {
        'FEED_URI': 'caring_house.csv',
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
        'authority': 'www.caring.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.xpath('//h2[contains(text()," by State")]/following-sibling::div['
                                   '@class="categories"]//li/a'):
            state_url = data.xpath('./@href').get()
            yield scrapy.Request(url=state_url, callback=self.get_city_url, headers=self.headers)

    def get_city_url(self, response):
        for data in response.css('div.lrtr-list-item a'):
            city_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=city_url, callback=self.get_listing_url, headers=self.headers)

    def get_listing_url(self, response):
        for data in response.css('div.form-group a.btn-secondary'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.xpath('//div[@itemprop="name"]/h1/text()').get('').strip()
        item['Business_Type'] = response.css('p.offers::text').get('').strip()
        item['Phone Number'] = response.xpath('//div[@itemprop="telephone"]/span/following-sibling::text()').get('').strip()
        item['Rating'] = response.css('div.inline-stars input::attr(value)').get('').strip()
        item['Reviews'] = response.css('div.inline-stars span::text').get('').replace('Reviews', '').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Senior Care'
        item['Source_URL'] = 'https://caring.com/senior-living/assisted-living/georgia/lilburn'
        item['Lead_Source'] = 'caring'
        yield item



