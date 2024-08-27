import scrapy


class HomelessshelterSpiderSpider(scrapy.Spider):
    name = 'homelessshelter_spider'
    start_urls = ['https://www.homelessshelterdirectory.org/']
    custom_settings = {
        'FEED_URI': 'homelessshelterdirectory.csv',
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
        for data in response.css('div.resp_1200 map area'):
            city_url = data.css('::attr(href)').get()
            yield response.follow(url=city_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('table tr td:nth-child(1) a'):
            list_url = data.css('::attr(href)').get()
            yield response.follow(url=list_url, callback=self.parse_list, headers=self.headers)

    def parse_list(self, response):
        for data in response.css('div.layout_post_2 h4 a'):
            item = dict()
            item['Business Name'] = data.css('::text').get('').strip()
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail,
                                      meta={'item': item}, headers=self.headers)
            else:
                item['Source_URL'] = 'https://www.homelessshelterdirectory.org/'
                item['Lead_Source'] = 'homelessshelterdirectory'
                item['Occupation'] = 'Homeless Shelter'
                yield item

    def parse_detail(self, response):
        item = response.meta['item']
        item['Phone Number'] = response.xpath('//a[contains(@href,"tel:")]/@href').get('').replace('tel:', '').strip()
        item['Street Address'] = response.xpath('//strong[contains(text(),'
                                                '"Address")]/following-sibling::br/following-sibling::text()').get('').replace('\r\n', '').strip()
        item['Email'] = response.xpath('//a[contains(@href,"mailto:")]/@href').get('').replace('mailto:', '').strip()
        item['Source_URL'] = 'https://www.homelessshelterdirectory.org/'
        item['Lead_Source'] = 'homelessshelterdirectory'
        item['Occupation'] = 'Homeless Shelter'
        item['Detail_Url'] = response.url
        yield item

