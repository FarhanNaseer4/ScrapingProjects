from datetime import datetime

import scrapy


class MountauburnhospitalSpiderSpider(scrapy.Spider):
    name = 'mountauburnhospital_spider'
    start_urls = ['https://www.mountauburnhospital.org/find-a-provider/search-results/?sort=7&page=1']
    custom_settings = {
        'FEED_URI': 'mountauburnhospital.csv',
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

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[0], callback=self.parse, headers=self.headers)

    def parse(self, response):
        for data in response.css('div.ProfileAnchorContainer a'):
            url = data.css('::attr(href)').get()
            item = dict()
            item['Meta_Description'] = response.xpath('//meta[@name="description" or '
                                                      '@property="og:description"]/@content').get('').strip()
            yield response.follow(url=url, callback=self.parse_detail, headers=self.headers, meta={'item': item})

        next_page = response.css('a.Next::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)

    def parse_detail(self, response):
        item = response.meta['item']
        fullname = response.css('span[itemprop="name"]::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['State'] = response.css('span[itemprop="addressRegion"] abbr::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Phone Number 1'] = response.css('span[itemprop="telephone"]::text').get('').strip()
        item['Phone Number'] = response.css('div[id="Summary"] p strong::text').get('').strip()
        item['Business_Site'] = response.css('div.field-name-field-listing-website a::attr(href)').get('').strip()
        item['Source_URL'] = 'https://www.mountauburnhospital.org/find-a-provider/search-results/?sort=7&page=1'
        item['Category'] = response.css('div[id="Specialities"] ul li::text').get('').strip()
        item['Occupation'] = 'Doctor'
        item['Lead_Source'] = 'mountauburnhospital'
        item['Detail_Url'] = response.url
        item['Record_Type'] = 'Person'
        item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        yield item
