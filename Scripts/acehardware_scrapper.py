import scrapy


class AcehardwareScrapperSpider(scrapy.Spider):
    name = 'acehardware_scrapper'
    start_urls = ['https://www.acehardware.com/store-directory']
    custom_settings = {
        'FEED_URI': 'acehardware_data.csv',
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
        'authority': 'www.acehardware.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'service-worker-navigation-preload': 'true',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.store-directory-list div.store-directory-list-item a'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.parse_data, headers=self.headers)

    def parse_data(self, response):
        item = dict()
        item['Business Name'] = response.css('span.store-banner-title-text::text').get('').strip()
        item['Full Name'] = response.css('div.store-information-bottom-wrap div.col-xs-4 div::text').get('').strip()
        item['Street Address'] = response.xpath('//div[@class="store-info-section"]/span[contains(text(), '
                                                '"Address")]/following::div[@class="store-details-text"]/span/text('
                                                ')').get('').strip()
        state_addres = response.xpath('//div[@class="store-info-section"]/span[contains(text(), '
                                      '"Address")]/following::div['
                                      '@class="store-details-text"]/span/br/following::text()').get('').strip()
        state_add = state_addres.split(',')
        if len(state_addres.split(',')) > 1:
            state_ab = state_add[1].strip().split(' ')
            if len(state_ab) > 1:
                item['State_Abrv'] = state_ab[0].strip()
                item['Zip'] = state_ab[1].strip()
        item['Phone Number'] = response.xpath('//div[@class="store-info-section"]/span[contains(text(), '
                                              '"Phone")]/following::a[@class="store-details-text"]/text()').get(
            '').strip()

        item['Email'] = response.css('div.store-info-right a.store-details-text::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://acehardware.com/store-directory'
        item['Occupation'] = 'Owner'
        item['Lead_Source'] = 'acehardware'
        item['Business_Type'] = 'Store'
        yield item
