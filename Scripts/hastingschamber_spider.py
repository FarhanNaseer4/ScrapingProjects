import scrapy


class HastingschamberSpiderSpider(scrapy.Spider):
    name = 'hastingschamber_spider'
    start_urls = ['https://business.hastingschamber.com/list/']
    custom_settings = {
        'FEED_URI': 'hastingschamber.csv',
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
        for data in response.css('div.gz-alphanumeric-btn a'):
            list_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=list_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div.card-header a'):
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('span.fl-heading-text::text').get('').strip()
        item['Occupation'] = response.css('span.gz-cat::text').get('').strip()
        item['Phone Number'] = response.css('span[itemprop="telephone"]::text').get('').strip()
        item['Business_Site'] = response.css('li.gz-card-website a::attr(href)').get('').strip()
        item['Full Name'] = response.css('div.gz-member-repname::text').get('').strip()
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['State_Abrv'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('li.gz-card-social a'))
        item['Source_URL'] = 'https://business.hastingschamber.com/list/'
        item['Lead_Source'] = 'business.hastingschamber'
        item['Detail_Url'] = response.url
        yield item
