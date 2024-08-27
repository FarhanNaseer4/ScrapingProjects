import scrapy


class ArizonafoodSpiderSpider(scrapy.Spider):
    name = 'arizonafood_spider'
    start_urls = ['https://arizonafoodservicenetwork.com/directory-main/']
    custom_settings = {
        'FEED_URI': 'arizonafood.csv',
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
        'authority': 'arizonafoodservicenetwork.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('td[data-align="center"] a'):
            main_url = data.css('::attr(href)').get()
            if 'directory-by-city-zip' not in main_url:
                yield scrapy.Request(url=main_url, callback=self.get_sub_category, headers=self.headers)

    def get_sub_category(self, response):
        for data in response.css('td[data-align="center"] a'):
            cate_url = data.css('::attr(href)').get()
            if 'directory-main' not in cate_url:
                yield scrapy.Request(url=cate_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('.cn-list-body div.cn-entry'):
            item = dict()
            item['Business Name'] = data.css('.cn-right h2 a::attr(title)').get('').strip()
            item['Detail_Url'] = data.css('.cn-right h2 a::attr(href)').get('').strip()
            item['Street Address'] = data.css('span.street-address::text').get('').strip()
            item['State'] = data.css('span.region::text').get('').strip()
            item['Zip'] = data.css('span.postal-code::text').get('').strip()
            item['Phone Number'] = data.css('span.cn-phone-number a::text').get('').strip()
            item['Business_Site'] = data.css('span.website a::text').get('').strip()
            item['Social_Media'] = ', '.join(social.css('::attr(href)').get() for social in data.css('span.social'
                                                                                                     '-media-network '
                                                                                                     'a'))
            item['Occupation'] = 'Food Service Network'
            item['Source_URL'] = 'https://arizonafoodservicenetwork.com/directory/pg/11/?cn-cat=771'
            item['Lead_Source'] = 'arizonafoodservicenetwork'
            yield item

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_listing, headers=self.headers)

