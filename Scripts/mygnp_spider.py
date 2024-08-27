import scrapy


class MygnpSpiderSpider(scrapy.Spider):
    name = 'mygnp_spider'
    start_urls = ['https://www.mygnp.com/pharmacies/']
    custom_settings = {
        'FEED_URI': 'mygnp.csv',
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
        for data in response.xpath('//h2[contains(text(),"by State")]/following-sibling::ul/li/a'):
            list_url = data.xpath('./@href').get()
            yield scrapy.Request(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.location-card'):
            item = dict()
            item['Business Name'] = data.css('p.location-title a::text').get('').strip()
            item['Detail_Url'] = data.css('p.location-title a::attr(href)').get('').strip()
            item['Street Address'] = data.xpath('./p[@class="location-title"]/following-sibling::p/text()').get(
                '').strip()
            state = data.xpath('./p[@class="location-title"]/following-sibling::p/br/following-sibling::text()').get(
                '').strip()
            if state:
                state_abb = state.split(',')[-1].strip()
                if state_abb:
                    item['State_Abrv'] = state_abb.split(' ')[0].strip()
                    item['Zip'] = state_abb.split(' ')[-1].strip()
            item['Phone Number'] = data.css('ul.icon-list li.icon-mobile a::text').get('').strip()
            item['Occupation'] = 'Pharmacy'
            item['Source_URL'] = 'https://www.mygnp.com/pharmacies/'
            item['Lead_Source'] = 'mygnp'
            yield item
