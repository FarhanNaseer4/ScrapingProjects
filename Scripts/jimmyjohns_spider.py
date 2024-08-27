import scrapy


class JimmyjohnsSpiderSpider(scrapy.Spider):
    name = 'jimmyjohns_spider'
    start_urls = ['https://www.jimmyjohns.com/find-a-jjs/?_ga=2.236154305.1507650124.1665985184-1351205464.1665985184']
    custom_settings = {
        'FEED_URI': 'jimmyjohns.csv',
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
        for data in response.css('div[id="store-info"] li a'):
            state_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=state_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('div.map-list-item-wrap a'):
            list_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.map-list-item'):
            item = dict()
            item['Business Name'] = data.css('span.location-name::text').get('').strip()
            item['Phone Number'] = data.css('a.phone::text').get('').strip()
            item['Street Address'] = data.css('div.address div:nth-child(1)::text').get('').strip()
            state = data.css('div.address div:nth-child(3)::text').get('').strip()
            if state:
                state_abb = state.split(',')[-1].strip()
                if len(state_abb.split(' ')) > 1:
                    item['State'] = state_abb.split(' ')[0].strip()
                    item['Zip'] = state_abb.split(' ')[-1].strip()
            detail_url = data.css('div.map-list-item-header a.ga-link::attr(href)').get().strip()
            if detail_url:
                item['Detail_Url'] = detail_url
            item['Occupation'] = 'JJ Stores'
            item['Lead_Source'] = 'jimmyjohns'
            item['Record_Type'] = 'Business'
            item['Source_URL'] = 'https://www.jimmyjohns.com/find-a-jjs'
            yield item



