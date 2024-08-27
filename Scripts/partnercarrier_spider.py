from datetime import datetime

import scrapy


class PartnercarrierSpiderSpider(scrapy.Spider):
    name = 'partnercarrier_spider'
    start_urls = ['https://partnercarrier.com/']

    custom_settings = {
        'FEED_URI': 'partnercarrier.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date', 'Meta_Description']
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.form-group a'):
            state_url = data.css('::attr(href)').get()
            if state_url:
                yield response.follow(url=state_url, callback=self.parse_county, headers=self.headers)

    def parse_county(self, response):
        for data in response.css('div.form-group a'):
            county_url = data.css('::attr(href)').get()
            if county_url:
                yield response.follow(url=county_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.div-border'):
            detail_url = data.css('div.col-md-12 a::attr(href)').get()
            item = dict()
            item['Street Address'] = data.xpath('.//div[@class="col-md-12"]/div[1]/text()[1]').get('').strip()
            state = data.xpath('.//div[@class="col-md-12"]/div[1]/text()[2]').get('').strip()
            if len(state.split(' ')) > 1:
                item['State'] = state.split(' ')[0].strip()
                item['Zip'] = state.split(' ')[-1].strip()
            item['Business Name'] = data.css('div a h4::text').get('').strip()
            item['Phone Number'] = data.css('div.col-xs-6 a::text').get('').strip()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers, meta={'item': item})

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_listing, headers=self.headers)

    def parse_detail(self, response):
        item = response.meta['item']
        item['Phone Number 1'] = response.xpath('//label[contains(text(),"Cell Phone")]/following-sibling::a/text()').get('').strip()
        business = response.xpath('//label[contains(text(),"Website")]/following-sibling::text()').get('').strip()
        if 'N/A' not in business:
            item['Business_Site'] = business
        email = response.xpath('//label[contains(text(),"Email")]/following-sibling::text()').get('').strip()
        if 'N/A' not in email:
            item['Email'] = email
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://partnercarrier.com/'
        item['Lead_Source'] = 'partnercarrier'
        item['Occupation'] = 'Trucking Company'
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item['Meta_Description'] = "The most comprehensive and up to date directory of 1,965,615 U.S. and Canadian " \
                                   "Trucking Companies and Freight Brokers. <a tabindex='0' role='button' " \
                                   "data-toggle='popover' data-html='true' data-trigger='focus' data-container='body' " \
                                   "data-placement='bottom' data-content='To see only hiring companies please select " \
                                   "'Companies Now Hiring' checkbox in the top-right corner of the page. <br " \
                                   "/>Trucking Company Owner / Operator ? Click the Login link in the top-right " \
                                   "corner of the page to create your account on PartnerCarrier.com and post your " \
                                   "trucking jobs free of charge.' class='link-font-size'> 509 Truck Driver Jobs</a>. " \
                                   "Search by location, service type, cargo type, company size and much more. Use the " \
                                   "map to define the area of your search. Let our unique algorithm suggest the best " \
                                   "Trucking Company or Freight Broker that suits your needs. "
        yield item
