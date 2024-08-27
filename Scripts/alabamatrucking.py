from datetime import datetime

import scrapy


class AlabamatruckingSpider(scrapy.Spider):
    name = 'alabamatrucking'
    start_urls = ['https://business.alabamatrucking.org/list/']

    custom_settings = {
        'FEED_URI': 'alabamatrucking.csv',
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
        for data in response.css('div[id="mn-alphanumeric"] a'):
            url = data.css('::attr(href)').get()
            item = dict()
            item['Meta_Description'] = response.xpath('//meta[@name="description" or '
                                                      '@property="og:description"]/@content').get('').strip()
            if url:
                yield response.follow(url=url, callback=self.parse_listing, headers=self.headers, meta={'item': item})

    def parse_listing(self, response):
        item = response.meta['item']
        for data in response.css('div[itemprop="name"] a'):
            detail_url = data.css('::attr(href)').get()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.detail_page, headers=self.headers,
                                      meta={'item': item})

    def detail_page(self, response):
        try:
            item = response.meta['item']
            item['Business Name'] = response.css('div.fixed h1::text').get('').strip()
            item['Street Address'] = response.css('div[itemprop="streetAddress"]::text').get('').strip()
            item['State'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
            item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
            item['Phone Number'] = response.css('div.mn-member-phone1::text').get('').strip()
            item['Phone Number 1'] = response.css('div.mn-member-phone2::text').get('').strip()
            item['Business_Site'] = response.css('div.mn-member-url a::attr(href)').get('').strip()
            item['Source_URL'] = 'https://business.alabamatrucking.org/list/'
            item['Occupation'] = response.css('ul.mn-member-cats li::text').get('').strip()
            item['Lead_Source'] = 'alabamatrucking'
            item['Detail_Url'] = response.url
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item
        except:
            print('Error')
