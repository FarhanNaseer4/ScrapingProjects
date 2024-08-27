import scrapy


class CsbnconnectSpiderSpider(scrapy.Spider):
    name = 'csbnconnect_spider'
    start_urls = ['https://www.csbnconnect.com/categories']
    base_url = 'https://www.csbnconnect.com{}'
    custom_settings = {
        'FEED_URI': 'csbnconnect.csv',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.xpath('//div[contains(@class,"col-md-3")]/a'):
            list_url = data.xpath('./@href').get()
            yield response.follow(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.member_box div.nopad a'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_listing, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('div.col-md-4 h2::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Services'
        item['Business_Site'] = response.xpath('//div[@class="col-md-8"]/a[contains(text(),"https")]/@href').get('').strip()
        address = response.css('span.location_text p::text').get('').strip()
        if address:
            item['Street Address'] = address.split(',')[0].strip()
        item['Category'] = response.css('div.col-md-12 span.primary_color_page::text').get('').strip()
        item['Phone Number'] = response.xpath('//a[contains(@href,"tel")]/@href').get('').replace('tel:', '').strip()
        item['Lead_Source'] = 'csbnconnect'
        item['Record_Type'] = 'Business'
        item['Source_URL'] = 'https://www.csbnconnect.com/categories'
        yield item
