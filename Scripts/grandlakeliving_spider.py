from datetime import datetime

import scrapy


class GrandlakelivingSpiderSpider(scrapy.Spider):
    name = 'grandlakeliving_spider'
    start_urls = ['https://grandlakeliving.com/grand-lake-business-directory/']
    custom_settings = {
        'FEED_URI': 'grandlakeliving.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date', 'Meta_Description']
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
        for data in response.css('div.cn-entry-cmap-card'):
            item = dict()
            item['Business Name'] = data.css('h2 span.org::text').get('').strip()
            item['Street Address'] = data.css('span.street-address::text').get('').strip()
            item['State'] = data.css('span.region::text').get('').strip()
            item['Zip'] = data.css('span.postal-code::text').get('').strip()
            item['First Name'] = data.css('span.contact-given-name::text').get('').strip()
            last = data.css('span.contact-family-name::text').get('').strip()
            if 'NMLS' in last:
                item['Last Name'] = last.split('-')[0].strip()
            else:
                item['Last Name'] = last
            item['Full Name'] = item['First Name'] + ' ' + item['Last Name']
            item['Phone Number'] = data.css('span.cn-phone-number a::text').get('').strip()
            item['Email'] = data.css('span.email-address a::text').get('').strip()
            item['Business_Site'] = data.css('span.website a.url::attr(href)').get('').strip()
            item['Source_URL'] = 'https://grandlakeliving.com/grand-lake-business-directory/'
            item['Lead_Source'] = 'grandlakeliving'
            item['Occupation'] = 'Business Service'
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['Meta_Description'] = 'Here you will find the most complete business directory for Oklahomas Grand ' \
                                       'Lake. You can search by business name or business category. '
            yield item

        next_page = response.css('a.next::attr(href)').get('').strip()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)



