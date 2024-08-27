import scrapy


class PinbuzSpiderSpider(scrapy.Spider):
    name = 'pinbuz_spider'
    start_urls = ['https://www.pinbuz.com/category/']

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
        for data in response.css('ul.tb li a'):
            cate_url = data.css('::attr(href)').get()
            item = dict()
            item['Occupation'] = data.css('::text').get('').strip()
            yield scrapy.Request(url=cate_url, meta={'item': item}, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        cate = response.meta['item']
        for data in response.css('div.home-list-pop'):
            item = dict()
            name = data.css('h3::text').get('').strip()
            if name:
                item['Business Name'] = name
                item['Occupation'] = cate.get('Occupation')
                item['Rating'] = data.css('h3 span::text').get('').strip()
                street = data.xpath('.//p/b[contains(text(),"Address")]/following-sibling::text()').get('').strip()
                if len(street.split(',')) > 1:
                    item['Street Address'] = street.split(',')[0].strip()
                item['Phone Number'] = data.xpath('.//div[@class="list-number"]//li/text()').get('').strip()
                item['Detail_Url'] = data.css('div.inn-list-pop-desc a::attr(href)').get('').strip()
                item['Source_URL'] = 'https://www.pinbuz.com/category/'
                item['Lead_Source'] = 'pinbuz'
                yield item

        next_url = response.xpath('//ul[@class="pagination"]/li[not(@class)]/a/@href').getall()
        for url in next_url:
            yield scrapy.Request(url=url, meta={'item': cate}, callback=self.parse_listing, headers=self.headers)
