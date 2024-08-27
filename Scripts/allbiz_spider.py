from datetime import datetime

import scrapy


class AllbizSpiderSpider(scrapy.Spider):
    name = 'allbiz_spider'
    start_urls = ['https://www.allbiz.com/']
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'HTTPERROR_ALLOW_ALL': True,
        'FEED_URI': 'allbiz.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date']
    }
    # custom_settings = {
    #     'FEED_URI': 'allbiz.csv',
    #     'FEED_FORMAT': 'csv',
    #     'FEED_EXPORT_ENCODING': 'utf-8-sig',
    #     'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
    #                            'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
    #                            'Business_Site', 'Social_Media', 'Record_Type',
    #                            'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
    #                            'Latitude', 'Longitude', 'Occupation',
    #                            'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
    #                            'SIC_Sectors', 'SIC_Categories',
    #                            'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date']
    # }
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('div.h-link-cont a'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('div.bname-b h1::text').get('').strip()
        fullname = response.css('p.detailed-header b::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        address = response.css('div.detailed-block address::text').get('').strip()
        if address:
            item['Street Address'] = address.split(',')[0].strip()
            state = address.split(',')[-1].strip()
            if len(state.split(' ')) > 1:
                item['State'] = state.split(' ')[0].strip()
                item['Zip'] = state.split(' ')[-1].strip()
            else:
                if state == 'USA':
                    state_abb = address.split(',')[-2].strip()
                    if state_abb:
                        item['State'] = state_abb.split(' ')[0].strip()
                        item['Zip'] = state_abb.split(' ')[-1].strip()
        item['Phone Number'] = response.xpath('//a[contains(@href,"tel")]/text()').get('').strip()
        item['Business_Site'] = response.css('a[title="Visit Webpage"]::attr(href)').get('').strip()
        item['Email'] = response.xpath('//a[contains(@href,"mailto")]/text()').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://www.allbiz.com/'
        item['Lead_Source'] = 'allbiz'
        item['Occupation'] = response.xpath('//b[contains(text(),"Title")]/following-sibling::text()').get('').strip()
        item['Record_Type'] = 'Business'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item

