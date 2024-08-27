import scrapy


class BestprosintownSpiderSpider(scrapy.Spider):
    name = 'bestprosintown_spider'
    start_urls = ['https://bestprosintown.com/']
    base_url = 'https://www.bestprosintown.com{}'
    custom_settings = {
        'FEED_URI': 'bestprosintown.csv',
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
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('div.tags a'):
            city_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=city_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        item = dict()
        for data in response.css('div.grid'):
            item['Business Name'] = data.css('div.wrapper h3 a::text').get()
            detail_url = data.css('div.wrapper h3 a::attr(href)').get()
            if detail_url:
                item['Detail_Url'] = self.base_url.format(detail_url)
            address = data.css('div.wrapper small::text').get()
            if address:
                if len(address.split(',')) > 1:
                    item['Street Address'] = address.split(',')[0].strip()
                    state = address.split(',')[-1].strip()
                    if len(state.split(' ')) > 1:
                        item['State'] = state.split(' ')[0].strip()
            item['Phone Number'] = data.css('div.phoneOrder a::text').get().strip()
            item['Reviews'] = data.css('div.score em::text').get('').replace('Reviews', '').strip()
            item['Rating'] = data.css('div.score strong::text').get('').strip()
            item['Source_URL'] = 'https://bestprosintown.com/co/silverthorne/summit-professional-services-/'
            item['Lead_Source'] = 'bestprosintown'
            item['Occupation'] = 'Local Services'
            yield item
