import scrapy


class OnuSpiderSpider(scrapy.Spider):
    name = 'onu_spider'
    request_url = 'https://www.onu.edu/directory?field_banner_last_name_value={}'
    first_name = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                  'U', 'V', 'W', 'X', 'Y', 'Z']
    next_page_url = 'https://www.onu.edu/directory?field_banner_last_name_value={}&page={}'
    base_url = 'https://www.onu.edu{}'
    custom_settings = {
        'FEED_URI': 'onu.csv',
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
        'authority': 'www.onu.edu',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def start_requests(self):
        for first in self.first_name:
            item = {'alph': first}
            yield scrapy.Request(url=self.request_url.format(first),meta={'item': item},
                                 callback=self.parse, headers=self.headers)

    def parse(self, response):
        item = response.meta['item']
        for data in response.css('table.cols-7 tr.col-sm-6'):
            detail_url = data.css('.views-field-field-banner-nickname a::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.parse_data, headers=self.headers)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            page_number = next_page.split('page=')[-1]
            yield scrapy.Request(url=self.next_page_url.format(item.get('alph', ''), page_number), meta={'item': item},
                                 callback=self.parse, headers=self.headers)

    def parse_data(self, response):
        item = dict()
        item['Full Name'] = response.css('div.field--name-field-banner-last-name .field__item::text').get('').strip()
        item['Street Address'] = response.xpath('//div[contains(@class,"field--name-field-banner-student-c-u-street1'
                                                '")]/div[@class="field__item"]/text()').get('').strip()
        oth_add = response.xpath('//div[contains(@class,"field--name-field-banner-student-c-u-street1")]/div['
                                 '@class="field__item"]/br/following::text()').get('').strip()
        if len(oth_add.split(',')) > 1:
            state_add = oth_add.split(',')[1].strip()
            if len(state_add.split(' ')) > 1:
                item['State_Abrv'] = state_add.split(' ')[0].strip()
        item['Email'] = response.css('div.field--name-field-banner-onu-email-address .field__item a::text').get('').strip()
        item['Occupation'] = 'Faculty & Staff'
        item['Source_URL'] = 'https://www.onu.edu/directory/'
        item['Lead_Source'] = 'onu.edu'
        item['Phone Number'] = response.css('div.field--name-field-banner-bu-phone .field__item::text').get('').strip()
        yield item
