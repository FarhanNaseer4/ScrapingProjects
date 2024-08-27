import scrapy


class IntentionalistSpiderSpider(scrapy.Spider):
    name = 'intentionalist_spider'
    start_urls = ['https://intentionalist.com/b/']
    base_url = 'https://intentionalist.com{}'
    # custom_settings = {
    #     'FEED_URI': 'intentionalist.csv',
    #     'FEED_FORMAT': 'csv',
    #     'FEED_EXPORT_ENCODING': 'utf-8-sig',
    #     'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
    #                            'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
    #                            'Business_Site', 'Social_Media',
    #                            'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
    #                            'Latitude', 'Longitude', 'Occupation',
    #                            'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
    #                            'SIC_Sectors', 'SIC_Categories',
    #                            'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
    # }
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'intentionalist.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation'],
        'HTTPERROR_ALLOW_ALL': True,
    }
    headers = {
        'authority': 'intentionalist.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36'
    }

    def parse(self, response):
        for data in response.css('div.column h5.entry-title a'):
            url = data.css('::attr(href)').get()
            yield scrapy.Request(url=url, callback=self.parse_data, headers=self.headers)

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)

    def parse_data(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.entry-title::text').get('').strip()
        item['Full Name'] = response.css('td.listing-custom-field-value::text').get('').strip()
        full_name = response.css('td.listing-custom-field-value::text').get('').strip()
        if len(full_name.split(' ')) > 1:
            item['First Name'] = full_name.split(' ')[0].strip()
            item['Last Name'] = full_name.split(' ')[1].strip()
        item['Phone Number'] = response.css('li.listing-phone a::text').get('').strip()
        item['Business_Site'] = response.css('li[id="listing-website"] a::attr(href)').get('').strip()
        item['Detail_Url'] = response.url
        street = response.css('div.listing-address-wrap a::text').get('').strip()
        if len(street.split(',')) > 2:
            item['Street Address'] = street.split(',')[0]
            state_add = street.split(',')[2].strip()
            if len(state_add.split(' ')) > 1:
                item['State_Abrv'] = state_add.split(' ')[0]
                item['Zip'] = state_add.split(' ')[1]
        item['Business_Type'] = 'Restaurants'
        item['Occupation'] = 'Owner'
        item['Source_URL'] = 'https://intentionalist.com/b/tag/minority-owned/'
        item['Lead_Source'] = 'intentionalist'
        yield item
