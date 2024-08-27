import scrapy


class HoodserveSpiderSpider(scrapy.Spider):
    name = 'hoodserve_spider'
    start_urls = ['https://hoodserve.com/categories']
    custom_settings = {
        'FEED_URI': 'hoodserve.csv',
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
        'authority': 'hoodserve.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('.row div.listing h3.pt-2 a'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.item-cover-title-section::text').get('').strip()
        item['Occupation'] = response.css('span.category::text').get('').strip()
        item['Street Address'] = response.xpath('//p[@class="item-cover-address-section"]/text()').get('').strip()
        state_add = response.xpath('//p[@class="item-cover-address-section"]/br/following::text()').get('').strip()
        if state_add:
            item['Zip'] = state_add.split(' ')[-1]
        item['Phone Number'] = response.xpath('//div[contains(@class,"item-cover-contact-section")]/h3//text()').get(
            '').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('div.item-cover'
                                                                                                 '-contact-section  '
                                                                                                 'p a'))
        item['Description'] = response.xpath('//div[@class="col-12"]/h4/following::p/text()').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://hoodserve.com/category/professional-services/state/indiana'
        item['Lead_Source'] = 'hoodserve'
        yield item
