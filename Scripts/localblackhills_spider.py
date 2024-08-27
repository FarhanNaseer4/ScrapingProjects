import scrapy


class LocalblackhillsSpiderSpider(scrapy.Spider):
    name = 'localblackhills_spider'
    start_urls = ['https://localblackhills.com/listing/categories']
    custom_settings = {
        'FEED_URI': 'localblackhills.csv',
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
        for data in response.css('u a.text-primary'):
            list_url = data.css('::attr(href)').get()
            yield response.follow(url=list_url, callback=self.parse_listing, headers=self.headers)

        next_page = response.xpath('//a[contains(text(),"Next")]/@href').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.media'):
            item = dict()
            item['Business Name'] = data.css('h3 a::text').get('').strip()
            item['Detail_Url'] = data.css('h3 a::attr(href)').get('').strip()
            item['Occupation'] = 'Business Service'
            item['Category'] = ', '.join(cate.css('::text').get('') for cate in data.css('p.categories-list a'))
            item['Street Address'] = data.xpath('.//address/p/text()').get('').strip()
            state = data.xpath('.//address/p/br/following-sibling::text()').get('').strip()
            if state:
                address = state.split(',')[-1].strip()
                if address:
                    item['Zip'] = address.split(' ')[-1].strip()
            item['Phone Number'] = data.css('p.contact-info a::text').get('').strip()
            item['Business_Site'] = data.css('p a.visit-website::attr(href)').get('').strip()
            item['Social_Media'] = ', '.join(social.css('::attr(href)').get('') for social in data.css('div.social-share a'))
            item['Lead_Source'] = 'localblackhills'
            item['Record_Type'] = 'Business'
            item['Source_URL'] = 'https://localblackhills.com/listing/categories'
            yield item
