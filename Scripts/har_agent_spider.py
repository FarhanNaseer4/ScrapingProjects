import scrapy


class HarAgentSpiderSpider(scrapy.Spider):
    name = 'har_agent_spider'
    start_urls = ['https://www.har.com/realestatepro']
    base_url = 'https://www.har.com{}'
    headers = {
        'authority': 'www.har.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    custom_settings = {
        'FEED_URI': 'har.csv',
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

    def parse(self, response):
        for data in response.css('div[id="agentsbycity"] a'):
            listing_url = data.css('::attr(href)').get()
            if not listing_url.startswith(self.base_url):
                listing_url = self.base_url.format(listing_url)
            yield scrapy.Request(url=listing_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('a.card--agent_longinfo'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.listing_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('div.text-truncate a::text').get('').strip()
        item['Detail_Url'] = response.url
        street = response.xpath('//div[contains(@class,"font_size--medium mb-5")]/text()').get('').strip()
        if len(street.split(',')) > 1:
            item['Street Address'] = street.split(',')[0].strip()
            state = street.split(',')[1].strip()
            if len(state.split(' ')) > 1:
                item['State_Abrv'] = state.split(' ')[0].strip()
                item['Zip'] = state.split(' ')[1].strip()
        item['Full Name'] = response.css('div.agentheader__agrow__ag__info_title h1::text').get('').strip()
        item['Phone Number'] = response.css('a[id="target_phone_header_1"]::text').get('').strip()
        item['Occupation'] = 'Agents'
        item['Source_URL'] = 'https://www.har.com/realestatepro'
        item['Lead_Source'] = 'har.com'
        yield item
