from datetime import datetime

import scrapy


class OglecountylifeSpiderSpider(scrapy.Spider):
    name = 'oglecountylife_spider'
    start_urls = ['https://oglecountylife.com/directory']
    custom_settings = {
        'FEED_URI': 'oglecountylife.csv',
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
        for data in response.css('div.classification a'):
            cate = data.css('::attr(href)').get()
            item = dict()
            item['Meta_Description'] = response.xpath('//meta[@name="description" or '
                                                      '@property="og:description"]/@content').get('').strip()
            if cate:
                yield response.follow(url=cate, callback=self.parse_listing, headers=self.headers, meta={'item': item})

    def parse_listing(self, response):
        meta_des = response.meta['item']
        for data in response.css('div.directoryListingAd'):
            item = dict()
            item['Business Name'] = data.css('h2 a::text').get('').strip()
            item['Detail_Url'] = data.css('h2 a::attr(htef)').get('').strip()
            address = data.xpath('.//span[contains(text(), "Address")]/following-sibling::text()').get('').strip()
            if len(address.split(',')) > 1:
                item['Street Address'] = address.split(',')[0].strip()
                state = address.split(',')[-1].strip()
                if len(state.split(' ')) == 2:
                    item['State'] = state.split(' ')[-1].strip()
            item['Phone Number'] = data.xpath('.//span[contains(text(), "Phone")]/following-sibling::text()').get('').strip()
            item['Meta_Description'] = meta_des.get('Meta_Description', '')
            item['Source_URL'] = 'https://oglecountylife.com/directory'
            item['Occupation'] = response.css('h2.directoryListingsHeader::text').get('').strip()
            item['Lead_Source'] = 'oglecountylife'
            item['Detail_Url'] = response.url
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item
