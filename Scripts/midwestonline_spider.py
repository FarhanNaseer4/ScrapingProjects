import scrapy


class MidwestonlineSpiderSpider(scrapy.Spider):
    name = 'midwestonline_spider'
    start_urls = ['https://www.midwestonline.us/local/']
    custom_settings = {
        'FEED_URI': 'midwestonline.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation', 'Record_Type',
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
        for data in response.css('ul.impcategories li a'):
            cate_url = data.css('::attr(href)').get()
            item = dict()
            item['occup'] = data.css('::attr(title)').get()
            yield scrapy.Request(url=cate_url, meta={'item': item}, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        item = response.meta['item']
        for data in response.css('div[data-listingcontainer="main"] div.newlstheading h3 a'):
            list_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=list_url, meta={'item': item}, callback=self.parse_detail, headers=self.headers)

        next_page = response.css('a[title="Next Page"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, meta={'item': item}, callback=self.parse_listing, headers=self.headers)

    def parse_detail(self, response):
        cate = response.meta['item']
        item = dict()
        item['Business Name'] = response.css('span.comp-name-top::text').get('').strip()
        item['Email'] = response.xpath('//a[contains(@href,"mailto:")]/@href').get('').replace('mailto:', '').strip()
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['State_Abrv'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Phone Number'] = response.css('span[data-attr="secondarycontactnospan"]::text').get('').strip()
        item['Full Name'] = response.xpath('//i[@class="icon-usermain"]/following-sibling::span/text()').get('').strip()
        item['Business_Site'] = response.css('a.company-website-url::attr(href)').get('').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get('') for data in response.css('ul.social-link'
                                                                                                   '-footer a'))
        item['Occupation'] = cate.get('occup')
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://www.midwestonline.us/local/'
        item['Lead_Source'] = 'midwestonline'
        yield item
