import scrapy


class CountyofficesSpiderSpider(scrapy.Spider):
    name = 'countyoffices_spider'
    start_urls = ['https://www.countyoffices.com/']
    custom_settings = {
        'FEED_URI': 'pinbuz.csv',
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
        for data in response.css('ul.state_list a'):
            state_url = data.css('::attr(href)').get()
            yield response.follow(url=state_url, callback=self.parse_county, headers=self.headers)

    def parse_county(self, response):
        for data in response.css('div.state-county-list a'):
            count_url = data.css('::attr(href)').get()
            yield response.follow(url=count_url, callback=self.parse_category, headers=self.headers)

    def parse_category(self, response):
        for data in response.css('div.county-offices-item a'):
            list_url = data.css('::attr(href)').get()
            yield response.follow(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.list-wrapper a'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.detail-heading::text').get('').strip()
        address = response.css('h2[itemprop="address"]::text').get('').strip()
        if address:
            item['Street Address'] = address.split(',')[0].strip()
            item['Zip'] = address.split(',')[-1].strip()
        item['State'] = response.xpath('//div[@class="item"]/span[contains(text(),"State")]/following-sibling::text()').get('').strip()
        item['Phone Number'] = response.xpath('//div[@itemprop="telephone"]/span/following-sibling::text()').get('').strip()
        item['Category'] = response.xpath('//div[@itemprop="department"]/span/following-sibling::text()').get('').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = 'County Office'
        item['Source_URL'] = 'https://www.countyoffices.com/'
        item['Lead_Source'] = 'countyoffices'
        yield item
