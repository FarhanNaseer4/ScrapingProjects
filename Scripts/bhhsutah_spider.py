from datetime import datetime

import scrapy


class BhhsutahSpiderSpider(scrapy.Spider):
    name = 'bhhsutah_spider'
    start_urls = ['https://www.bhhsutah.com/agents/']
    custom_settings = {
        'FEED_URI': 'bhhsutah.csv',
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

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.details  div.btnset a'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        fullname = response.css('div.small-12 h1::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        address = response.css('li.location span::text').get()
        if address:
            item['Street Address'] = address.split(',')[0].strip()
            item['Zip'] = address.split(',')[-1].strip()
        item['State_Abrv'] = response.css('li.office a::text').get('').strip()
        item['Phone Number'] = response.css('li.cellphone span::text').get('').strip()
        item['Business_Site'] = response.css('li.website a::attr(href)').get('').strip()
        item['Email'] = response.css('li.email a::text').get('').strip()
        item['Source_URL'] = 'https://www.bhhsutah.com/agents/'
        item['Occupation'] = 'Realtor'
        item['Lead_Source'] = 'bhhsutah'
        item['Detail_Url'] = response.url
        item['Record_Type'] = 'Person'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item
