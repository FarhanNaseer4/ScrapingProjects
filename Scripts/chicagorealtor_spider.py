import json

import scrapy


class ChicagorealtorSpiderSpider(scrapy.Spider):
    name = 'chicagorealtor_spider'
    start_urls = ['https://chicagorealtor.com/realtor-search/']
    base_url = 'https://chicagorealtor.com{}'
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'chicagorealtor.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'HTTPERROR_ALLOW_ALL': True,
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
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'X-Crawlera-Profile': 'pass',
        'X-Crawlera-Region': 'us'
    }

    def parse(self, response):
        for data in response.css('tr.vcard'):
            detail_url = data.css('td.realtor_number a::attr(href)').get()
            if detail_url:
                yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)
        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse, headers=self.headers)

    def detail_page(self, response):
        json_obj = response.css('script[type="application/json"]::text').get()
        result = json.loads(json_obj)
        agent_data = result.get('props', {}).get('pageProps', {})
        personal_info = agent_data.get('jsonld', {}).get('content', {})
        address_info = agent_data.get('agentDetails', {}).get('address', {})
        item = dict()
        item['Business Name'] = personal_info.get('officeName', '')
        item['Full Name'] = personal_info.get('agentName', '')
        item['Description'] = personal_info.get('description', '')
        item['State'] = address_info.get('city', '')
        item['Zip'] = address_info.get('postal_code', '')
        item['State_Abrv'] = address_info.get('state_code', '')
        item['Street Address'] = address_info.get('line', '')
        item['Detail_Url'] = response.url
        item['Phone Number'] = personal_info.get('telephone', '')
        item['Occupation'] = 'Realtor'
        item['Source_URL'] = 'https://chicagorealtor.com/'
        item['Lead_Source'] = 'chicagorealtor'
        yield item
