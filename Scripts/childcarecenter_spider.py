import scrapy


class ChildcarecenterSpiderSpider(scrapy.Spider):
    name = 'childcarecenter_spider'
    start_urls = ['https://childcarecenter.us/state']
    custom_settings = {
        'FEED_URI': 'childcarecenter.csv',
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
        for data in response.css('map[id="map"] area'):
            city_url = data.css('::attr(href)').get()
            yield response.follow(url=city_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('div.cities a'):
            list_url = data.css('::attr(href)').get()
            yield response.follow(url=list_url, callback=self.parse_list, headers=self.headers)

    def parse_list(self, response):
        for data in response.xpath('//div[@class="up-section head"]'):
            item = dict()
            phone = data.xpath('.//h3/following-sibling::span/text()').get()
            if phone:
                if len(phone.split('|')) > 1:
                    item['Phone Number'] = phone.split('|')[-1].strip()
            item['Business Name'] = data.xpath('.//h3/a/text()').get('').strip()
            detail_url = data.xpath('.//h3/a/@href').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail,
                                      meta={'item': item}, headers=self.headers)
            else:
                item['Source_URL'] = 'https://childcarecenter.us/state'
                item['Lead_Source'] = 'childcarecenter.us'
                item['Occupation'] = 'Child Care Center'
                yield item

    def parse_detail(self, response):
        item = response.meta['item']
        address = response.xpath('//i[@class="zmdi zmdi-pin"]/following-sibling::text()').get()
        if address:
            item['Street Address'] = address.split(',')[0].strip()
            state = address.split(',')[-1].strip()
            if state:
                item['Zip'] = state.split(' ')[-1].strip()
        item['Business_Site'] = response.xpath('//i[@class="zmdi zmdi-globe-alt"]/following-sibling::a/@href').get('').strip()
        item['Source_URL'] = 'https://childcarecenter.us/state'
        item['Lead_Source'] = 'childcarecenter.us'
        item['Occupation'] = 'Child Care Center'
        item['Detail_Url'] = response.url
        yield item


