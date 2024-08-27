import scrapy


class DestinationSpiderSpider(scrapy.Spider):
    name = 'destination_spider'
    start_urls = ['https://destinationsmalltown.com/businesses']
    custom_settings = {
        'FEED_URI': 'destinationsmalltown.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
    }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('div.my-1 a.text-green'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, headers=self.headers)

        next_page = response.xpath('//a[contains(text(),"Next")]/@href').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.title::text').get('').strip()
        item['Business_Type'] = response.css('ul.mt-4 a.text-blue-green::text').get('').strip()
        item['Business_Site'] = response.css('ul.mt-6 a.flex-1::attr(href)').get('').strip()
        item['Email'] = response.xpath('//a[contains(@href,"@")]/text()').get('').strip()
        item['Phone Number'] = response.xpath('//a[contains(@href,"tel")]/text()').get('').strip()
        item['Street Address'] = response.xpath('//div[contains(@class,"px-4")]/p/text()').get('').strip()
        state = response.xpath('//div[contains(@class,"px-4")]/p/br/following-sibling::text()').get('').strip()
        if len(state.split(',')) > 1:
            state_abb = state.split(',')[-1].strip()
            if len(state_abb.split(' ')) > 1:
                item['State'] = state_abb.split(' ')[0].strip()
                item['Zip'] = state_abb.split(' ')[-1].strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://destinationsmalltown.com/businesses'
        item['Lead_Source'] = 'destinationsmalltown'
        item['Occupation'] = "Business Service"
        item['Record_Type'] = 'Business'
        yield item
