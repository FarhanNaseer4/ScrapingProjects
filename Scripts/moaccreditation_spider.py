from datetime import datetime

import scrapy


class MoaccreditationSpiderSpider(scrapy.Spider):
    name = 'moaccreditation_spider'
    start_urls = ['https://marit.moaccreditation.org/directory/index']
    custom_settings = {
        'FEED_URI': 'moaccreditation.csv',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.xpath('//div[contains(@class,"directoryListing")]'):
            item = dict()
            item['Meta_Description'] = response.xpath('//meta[@name="description" or '
                                                      '@property="og:description"]/@content').get('').strip()
            address = data.xpath('./br/following-sibling::text()').get()
            if address:
                item['Street Address'] = address.split(',')[0].strip()
                state = address.split(',')[-1].strip()
                if len(state.split(' ')) > 1:
                    item['State'] = state.split(' ')[0].strip()
                    item['Zip'] = state.split(' ')[-1].strip()
            detail_url = data.xpath('./a/@href').get()
            item['Business Name'] = data.xpath('./a/text()').get('').strip()
            yield response.follow(url=detail_url, callback=self.parse_detail, meta={'item': item}, headers=self.headers)

        next_page = response.css('a.nextLink::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)

    def parse_detail(self, response):
        item = response.meta['item']
        item['Phone Number'] = response.css('div[aria-labelledby="telephone-label"]::text').get('').strip()
        item['Business_Site'] = response.xpath('//label[@for="website"]/following-sibling::div/text()').get('').strip()
        data = response.css('div.fieldcontain div p::text').get('').strip()
        fullname = data.split('(')[0].strip()
        email = data.split('(')[-1].strip()
        if email:
            item['Email'] = email.replace(')', '').strip()
        if fullname:
            item['Full Name'] = fullname.strip()
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Source_URL'] = 'https://marit.moaccreditation.org/directory/index'
        item['Occupation'] = 'Program Director'
        item['Lead_Source'] = 'marit.moaccreditation'
        item['Detail_Url'] = response.url
        item['Record_Type'] = 'Person'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item

