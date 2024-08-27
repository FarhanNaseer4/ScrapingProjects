import scrapy


class AgcetnSpiderSpider(scrapy.Spider):
    name = 'agcetn_spider'
    start_urls = ['https://business.agcetn.org/list']

    custom_settings = {
        'FEED_URI': 'agcetn.csv',
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
        for data in response.css('div[id="mn-alphanumeric"] a'):
            url = data.css('::attr(href)').get()
            yield scrapy.Request(url=url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div[itemprop="name"] a'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('div.wsite-section-elements h2::text').get('').strip()
        item['Street Address'] = response.css('div[itemprop="streetAddress"]::text').get('').strip()
        item['State'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Phone Number'] = response.css('div.mn-member-phone1::text').get('').strip()
        item['Phone Number 1'] = response.css('div.mn-member-phone2::text').get('').strip()
        item['Business_Site'] = response.css('div.mn-member-url a::attr(href)').get('').strip()
        fullname = response.css('div.mn-member-repname::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()

        item['Source_URL'] = 'https://business.agcetn.org/list'
        item['Occupation'] = response.css('ul.mn-member-cats li::text').get('').strip()
        item['Lead_Source'] = 'agcetn'
        item['Record_Type'] = 'Business'
        item['Detail_Url'] = response.url
        yield item
