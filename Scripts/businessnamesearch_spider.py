import scrapy


class BusinessnamesearchSpiderSpider(scrapy.Spider):
    name = 'businessnamesearch_spider'
    start_urls = ['https://www.businessnamesearch.org/']
    base_url = 'https://www.businessnamesearch.org{}'
    custom_settings = {
        'FEED_URI': 'businessnamesearch.csv',
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    }

    def parse(self, response):
        for data in response.css('div.home-states-wrap ul li a'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            yield scrapy.Request(url=state_url, callback=self.parse_county_url, headers=self.headers)

    def parse_county_url(self, response):
        for data in response.xpath('//div[contains(@class,"list-group")]/h2[contains(text(), "Search by '
                                   'County")]/following::ul/li/a'):
            county_url = data.xpath('./@href').get()
            if not county_url.startswith(self.base_url):
                county_url = self.base_url.format(county_url)
            yield scrapy.Request(url=county_url, callback=self.parse_listing_data, headers=self.headers)

    def parse_listing_data(self, response):
        for data in response.css('p.condensed-listing'):
            item = dict()
            item['Business Name'] = data.css('span.name::text').get('').strip()
            item['Street Address'] = data.css('span.address::text').get('').strip()
            item['State'] = data.css('span.city-state::text').get('').strip()
            item['Zip'] = data.css('span.zipcode::text').get('').strip()
            item['Phone Number'] = data.css('a.phone::text').get('').strip()
            item['Occupation'] = 'Business Services'
            item['Source_URL'] = 'https://businessnamesearch.org/'
            item['Lead_Source'] = 'businessnamesearch'
            yield item


