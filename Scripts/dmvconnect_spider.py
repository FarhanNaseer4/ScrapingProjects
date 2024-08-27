import scrapy


class DmvconnectSpiderSpider(scrapy.Spider):
    name = 'dmvconnect_spider'
    start_urls = ['https://dmvconnect.com/']
    base_url = 'https://dmvconnect.com{}'
    custom_settings = {
        'FEED_URI': 'dmvconnect.csv',
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
        'authority': 'dmvconnect.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.states a'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            yield scrapy.Request(url=state_url, callback=self.get_office_url, headers=self.headers)

    def get_office_url(self, response):
        for data in response.css('table.table-striped tr td:nth-child(2) a'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('dd.name::text').get('').strip()
        item['Street Address'] = response.css('span.streetAddress::text').get('').strip()
        item['State'] = response.css('span.addressRegion::text').get('').strip()
        item['Zip'] = response.css('span.postalCode::text').get('').strip()
        item['Phone Number'] = response.css('dd.telephone::text').get('').strip()
        item['Rating'] = response.css('span[itemprop="ratingValue"]::text').get('').strip()
        item['Reviews'] = response.css('span[itemprop="reviewCount"]::text').get('').strip()
        item['Description'] = response.css('div.content p::text').get('').strip()
        item['Occupation'] = 'DMV Office'
        item['Source_URL'] = 'https://dmvconnect.com/'
        item['Lead_Source'] = 'dmvconnect'
        item['Detail_Url'] = response.url
        yield item
