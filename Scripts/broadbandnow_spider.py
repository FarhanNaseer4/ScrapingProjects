import scrapy


class BroadbandnowSpiderSpider(scrapy.Spider):
    name = 'broadbandnow_spider'
    start_urls = ['https://broadbandnow.com/']

    custom_settings = {
        'FEED_URI': 'broadbandnow.csv',
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
        'authority': 'broadbandnow.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('ul.state-list li a'):
            state_url = data.css('::attr(href)').get()
            yield response.follow(url=state_url, callback=self.city_page, headers=self.headers)

    def city_page(self, response):
        for data in response.css('table.sortable-table tr td:nth-child(1) a'):
            city_url = data.css('::attr(href)').get()
            yield response.follow(url=city_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div.js-provider-card'):
            item = dict()
            item['Business Name'] = data.css('::attr(data-provider)').get('').strip()
            item['Description'] = data.css('::attr(data-gtm-speed)').get('').strip()
            item['Detail_Url'] = data.css('a.d-provider-card__logo-wrapper::attr(href)').get()
            item['Phone Number'] = data.css('a.btn--secondary-outline-pink::attr(href)').get('').replace('tel:', '').strip()
            item['Occupation'] = 'Internet Providers'
            item['Source_URL'] = 'https://broadbandnow.com/Kansas/Mound-City'
            item['Lead_Source'] = 'broadbandnow'
            yield item

