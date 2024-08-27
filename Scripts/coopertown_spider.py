from datetime import datetime

import scrapy


class CoopertownSpiderSpider(scrapy.Spider):
    name = 'coopertown_spider'
    start_urls = ['https://coopertown.tennesseeonline.us/local']
    custom_settings = {
        'FEED_URI': 'coopertown_tennesseeonline.csv',
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
        for data in response.css('div[id="top-cat-list"] ul li a'):
            list_url = data.css('::attr(href)').get()
            if list_url:
                yield response.follow(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.listBack_wrp h3 a'):
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_details, headers=self.headers)

        next_page = response.css('li.navigate-page-btn a::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_listing, headers=self.headers)

    def parse_details(self, response):
        item = dict()
        item['Business Name'] = response.css('div.company-name span.comp-name-top::text').get('').strip()
        fullname = response.xpath('//i[@class="icon-usermain"]/following-sibling::span/text()').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['State'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Phone Number'] = response.css('span[data-attr="secondarycontactnospan"]::text').get('').strip()
        item['Email'] = response.xpath('//i[@title="Email Id"]/following-sibling::span/text()').get('').strip()
        item['Business_Site'] = response.css('a.company-website-url::attr(href)').get()
        item['Source_URL'] = 'https://coopertown.tennesseeonline.us/local'
        item['Lead_Source'] = 'coopertown.tennesseeonline'
        item['Occupation'] = response.css('ul[data-element="listing-categories-ul"] li a::text').get()
        item['Meta_Description'] = ''
        item['Record_Type'] = 'Person'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item
