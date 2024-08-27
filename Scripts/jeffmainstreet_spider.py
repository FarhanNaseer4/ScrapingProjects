import scrapy


class JeffmainstreetSpiderSpider(scrapy.Spider):
    name = 'jeffmainstreet_spider'
    start_urls = ['https://www.jeffmainstreet.org/jeffersonville-buy-local-directory/']
    custom_settings = {
        'FEED_URI': 'jeffmainstreet.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.entry-content ul span a'):
            cate_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=cate_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div[id="businesslist"] div.type-business'):
            item = dict()
            item['Business Name'] = data.css('h3 a::text').get('').strip()
            detail_url = data.css('h3 a::attr(href)').get()
            item['Street Address'] = data.xpath('.//p[@class="address"]/text()').get('').strip()
            item['Description'] = data.css('div.description span.bus_content::text').get('').strip()
            item['Phone Number'] = data.css('p.phone a::text').get('').strip()
            item['Business_Site'] = data.css('p.website a::attr(href)').get('').strip()
            item['Social_Media'] = ', '.join(link.css('::attr(href)').get('') for link in data.css('div.cdash-social-media ul li a'))

            yield scrapy.Request(url=detail_url, meta={'item': item}, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = response.meta['item']
        item['Occupation'] = 'Business Services'
        item['Source_URL'] = 'https://www.jeffmainstreet.org/jeffersonville-buy-local-directory/'
        item['Lead_Source'] = 'jeffmainstreet'
        item['Detail_Url'] = response.url
        item['Category'] = response.css('p.categories a::text').get('').strip()
        yield item
