import scrapy


class PlainfieldSpiderSpider(scrapy.Spider):
    name = 'plainfield_spider'
    start_urls = ['https://web.plainfield-in.com/allcategories']
    base_url = 'https://web.plainfield-in.com{}'
    custom_settings = {
        'FEED_URI': 'plainfield.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
    }
    headers = {
        'authority': 'web.plainfield-in.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('li.ListingCategories_AllCategories_CATEGORY a'):
            item = dict()
            detail_url = data.css('::attr(href)').get()
            item['Occupation'] = data.css('::text').get('').strip()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.parse_listing,
                                 meta={'item': item}, headers=self.headers)

    def parse_listing(self, response):
        item = response.meta['item']
        for data in response.css('div.ListingResults_All_CONTAINER'):
            item['Business Name'] = data.css('span[itemprop="name"] a::text').get('').strip()
            item['Street Address'] = data.css('span[itemprop="street-address"]::text').get('').strip()
            item['State'] = data.css('span[itemprop="locality"]::text').get('').strip()
            item['State_Abrv'] = data.css('span[itemprop="region"]::text').get('').strip()
            item['Zip'] = data.css('span[itemprop="postal-code"]::text').get('').strip()
            fullname = data.xpath('.//div[@class="ListingResults_Level3_MAINCONTACT"]//text()').get('').strip()
            item['Full Name'] = fullname
            if fullname:
                if len(fullname.split(' ')) > 2:
                    item['First Name'] = fullname.split(' ')[0].strip()
                    item['Last Name'] = fullname.split(' ')[2].strip()
                else:
                    if len(fullname.split(' ')) > 1:
                        item['First Name'] = fullname.split(' ')[0].strip()
                        item['Last Name'] = fullname.split(' ')[1].strip()
                    else:
                        item['First Name'] = fullname.split(' ')[0].strip()
                        item['Last Name'] = ''
            item['Phone Number'] = data.xpath('.//div[@class="ListingResults_Level3_PHONE1"]//text()').get('').strip()
            item['Detail_Url'] = self.base_url.format(data.css('span[itemprop="name"] a::attr(href)').get())
            item['Source_URL'] = 'https://web.plainfield-in.com/search'
            item['Lead_Source'] = 'web.plainfield-in'
            yield item



