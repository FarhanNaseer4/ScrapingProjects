from datetime import datetime

import scrapy


class MasoncitySpiderSpider(scrapy.Spider):
    name = 'masoncity_spider'
    start_urls = ['https://masoncity.net/staff.aspx']
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'FEED_URI': 'masoncity.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date'],
        'HTTPERROR_ALLOW_ALL': True,
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
        for data in response.css('div.StaffEntry'):
            item = dict()
            fullname = data.css('span.spanHeader::text').get('').strip()
            if fullname:
                item['Full Name'] = fullname
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = fullname.split(' ')[-1].strip()
            item['Phone Number'] = data.css('div.col-md-2::text').get('').strip()
            item['Email'] = data.css('div.col-lg-2 a::attr(href)').get('').replace('mailto:', '').strip()
            item['Source_URL'] = 'https://masoncity.net/staff.aspx'
            item['Occupation'] = data.css('div.col-lg-5::text').get('').strip()
            item['Lead_Source'] = 'masoncity'
            item['Record_Type'] = 'Person'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item

