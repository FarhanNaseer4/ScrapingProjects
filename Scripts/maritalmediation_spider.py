from datetime import datetime

import scrapy


class MaritalmediationSpiderSpider(scrapy.Spider):
    name = 'maritalmediation_spider'
    start_urls = ['https://www.maritalmediation.com/mediator-directory/wpbdm-category/marital-mediators/']
    custom_settings = {
        'FEED_URI': 'maritalmediation.csv',
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
        for data in response.css('div.wpbdp-listing'):
            item = dict()
            fullname = data.css('div.listing-title a::text').get('').strip()
            if fullname:
                item['Full Name'] = fullname
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = fullname.split(' ')[-1].strip()
            detail_url = data.css('div.listing-title a::attr(href)').get()
            if detail_url:
                item['Detail_Url'] = detail_url
            item['Meta_Description'] = response.xpath('//meta[@name="description" or '
                                                      '@property="og:description"]/@content').get('').strip()
            item['Business Name'] = data.css('div.wpbdp-field-company_name span.value::text').get('').strip()
            item['Phone Number'] = data.css('div.wpbdp-field-business_phone_number span.value::text').get('').strip()
            item['Street Address'] = data.css('div.wpbdp-field-city span.value::text').get('').strip()
            item['State'] = data.css('div.wpbdp-field-state_abbreviation span.value::text').get('').strip()
            item['Source_URL'] = 'https://www.maritalmediation.com/mediator-directory/wpbdm-category/marital-mediators/'
            item['Lead_Source'] = 'maritalmediation'
            item['Occupation'] = 'Marital Mediators'
            item['Record_Type'] = 'Person'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item

        next_page = response.css('a.nextpostslink::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)
