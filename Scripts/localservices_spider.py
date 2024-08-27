import scrapy


class LocalservicesSpiderSpider(scrapy.Spider):
    name = 'localservices_spider'
    start_urls = ['https://localservices.sulekha.com/all-category']
    base_url = 'https://localservices.sulekha.com{}'
    custom_settings = {
        'FEED_URI': 'localservices_sulekha.csv',
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
        'authority': 'localservices.sulekha.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('article.list_col h4 a'):
            listing_url = data.css('::attr(href)').get()
            if not listing_url.startswith(self.base_url):
                listing_url = self.base_url.format(listing_url)
            yield scrapy.Request(url=listing_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div[id="divaddviewmore"] h3.media-heading a'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.css('a[title="Next"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.listing_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('h1[itemprop="name"]::text').get('').strip()
        item['Occupation'] = 'Business Service'
        item['Phone Number'] = response.css('a.phonepin::text').get('').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('div.social-outs li a'))
        item['Full Name'] = response.css('li.busi-name::text').get('').strip()
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['State_Abrv'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Reviews'] = response.css('span[itemprop="reviewCount"]::text').get('').strip()
        item['Source_URL'] = 'https://localservices.sulekha.com/financial-legal-services-in-austin-tx'
        item['Lead_Source'] = 'localservices_sulekha'
        yield item

