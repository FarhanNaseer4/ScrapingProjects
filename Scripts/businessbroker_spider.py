import scrapy


class BusinessbrokerSpiderSpider(scrapy.Spider):
    name = 'businessbroker_spider'
    start_urls = ['https://www.businessbroker.net/brokers/brokers.aspx']
    base_url = 'https://www.businessbroker.net{}'
    custom_settings = {
        'FEED_URI': 'businessbroker.csv',
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
        'authority': 'www.businessbroker.net',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('ul.categories li a'):
            url = data.css('::attr(href)').get()
            if not url.startswith(self.base_url):
                url = self.base_url.format(url)
            yield scrapy.Request(url=url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('.columns div.broker'):
            detail_url = data.css('p.company a::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.parse_data, headers=self.headers)

    def parse_data(self, response):
        item = dict()
        fullname = response.css('h1.white-text::text').get('').strip()
        item['Full Name'] = fullname
        if len(fullname.split(' ')) > 2:
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[2].strip()
        else:
            if len(fullname.split(' ')) > 1:
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = fullname.split(' ')[1].strip()
        item['Street Address'] = response.css('div.address p.white-text:nth-child(2)::text').get('').strip()
        state = response.css('div.address p.white-text:nth-child(3)::text').get('').strip()
        if len(state.split(',')) > 1:
            item['State'] = state.split(',')[0].strip()
            state_zip = state.split(',')[1].strip()
            if len(state_zip.split(' ')) > 1:
                item['State_Abrv'] = state_zip.split(' ')[0].strip()
                item['Zip'] = state_zip.split(' ')[1].strip()
        item['Phone Number'] = response.css('div.brokerPhone p::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Broker'
        item['Source_URL'] = 'https://businessbroker.net/business-for-sale/restaurant-bar-edgewood-iowa/553380.aspx'
        item['Lead_Source'] = 'businessbroker'
        yield item
