from datetime import datetime

import scrapy


class OmcaokSpiderSpider(scrapy.Spider):
    name = 'omcaok_spider'
    start_urls = ['https://www.omcaok.com/directory/']
    custom_settings = {
        'FEED_URI': 'omcaok.csv',
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('div.vc_gitem-zone-mini'):
            item = dict()
            item['Business Name'] = data.css('div.vc_custom_heading p::text').get('').strip()
            address = data.css('div.field_5e5443465ece2::text').get('').strip()
            if address:
                item['Street Address'] = address.split(',')[0].strip()
                state = address.split(',')[-1].strip()
                if state:
                    item['State'] = state.split(' ')[0].strip()
                    item['Zip'] = state.split(' ')[-1].strip()
            item['Phone Number'] = data.css('div.field_5e54435a5ece3::text').get('').strip()
            item['Business_Site'] = data.xpath('.//span[contains(text(),"Website")]/following-sibling::text()').get('').strip()
            item['Category'] = data.css('div.field_5e54442b5ece8::text').get('').strip()
            item['Detail_Url'] = response.url
            item['Source_URL'] = 'https://www.omcaok.com/directory/'
            item['Lead_Source'] = 'omcaok'
            item['Occupation'] = 'Corporate Member'
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item



