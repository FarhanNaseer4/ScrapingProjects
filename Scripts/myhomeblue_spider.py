import scrapy


class MyhomeblueSpiderSpider(scrapy.Spider):
    name = 'myhomeblue_spider'
    start_urls = ['https://www.myhomeblueridge.com/categories']

    custom_settings = {
        'FEED_URI': 'myhomeblueridge.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
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
        for data in response.css('div.sabai-directory-category-title a'):
            list_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.sabai-directory-main'):
            item = dict()
            item['Business Name'] = data.css('.sabai-directory-title a::attr(title)').get('').strip()
            item['Detail_Url'] = data.css('.sabai-directory-title a::attr(href)').get('').strip()
            address = data.xpath('.//div[@class="sabai-directory-location"]/span//text()').get('').strip()
            if address:
                item['Street Address'] = address.split(',')[0].strip()
            item['Phone Number'] = data.css('span[itemprop="telephone"]::text').get('').strip()
            item['Category'] = data.xpath('.//div[@class="sabai-directory-category"]/a/text()').get('').strip()
            item['Business_Site'] = data.css('div.sabai-directory-contact-website a::attr(href)').get('').strip()
            item['Source_URL'] = 'https://www.myhomeblueridge.com/categories'
            item['Occupation'] = 'Business Service'
            item['Lead_Source'] = 'myhomeblueridge'
            item['Record_Type'] = 'Business'
            yield item

