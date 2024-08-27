import scrapy


class PlaceviewerSpiderSpider(scrapy.Spider):
    name = 'placeviewer_spider'
    start_urls = ['https://placeviewer.net/']
    custom_settings = {
        'FEED_URI': 'placeviewer.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
    }
    headers = {
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('ul.catelist li a'):
            list_url = data.css('::attr(href)').get()
            item = dict()
            item['Occupation'] = data.xpath('./text()').get('').strip()
            yield response.follow(url=list_url, callback=self.parse_listing,
                                  meta={'item': item}, headers=self.headers)

    def parse_listing(self, response):
        item = response.meta['item']
        for data in response.css('div.jobinfo h3 a'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail,
                                  meta={'item': item}, headers=self.headers)

        next_page = response.css('a.nextposts-link::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_listing,
                                  meta={'item': item}, headers=self.headers)

    def parse_detail(self, response):
        item = response.meta['item']
        item['Business Name'] = response.css('h1.title::text').get('').strip()

        street = response.xpath('//i[contains(@class,"fa-map-marker")]/following-sibling::text()').get('').strip()
        if street:
            item['Street Address'] = street.split(',')[0].strip()
        item['State'] = response.xpath('//b[contains(text(),"State")]/following-sibling::span/a/text()').get('').strip()
        item['Zip'] = response.xpath('//b[contains(text(),"Zip Code")]/following-sibling::span/text()').get('').replace(':', '').strip()
        item['Phone Number'] = response.xpath('//a[contains(@href,"tel:")]/text()').get('').strip()
        item['Email'] = response.xpath('//span[contains(text(),"@")]/text()').get('').replace(':', '').strip()
        item['Business_Site'] = response.xpath('//b[contains(text(),"Website")]/following-sibling::span/text()').get('').replace(':', '').strip()
        item['Social_Media'] = ', '.join(
            data.css('::attr(href)').get() for data in response.css('div.cadsocial a'))
        item['Source_URL'] = 'https://placeviewer.net/'
        item['Lead_Source'] = 'placeviewer'
        item['Detail_Url'] = response.url
        item['Record_Type'] = 'Business'
        yield item


