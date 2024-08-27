import scrapy


class GeorgiagrownSpiderSpider(scrapy.Spider):
    name = 'georgiagrown_spider'
    start_urls = ['https://georgiagrown.com/membership/member-directory/']
    next = 'https://georgiagrown.com/membership/member-directory/page/{}'
    custom_settings = {
        'FEED_URI': 'georgiagrown.csv',
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
        'authority': 'georgiagrown.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def start_requests(self):
        item = {'page': 1}
        yield scrapy.Request(url=self.start_urls[0], meta={'item': item}, callback=self.parse, headers=self.headers)

    def parse(self, response):
        page_info = response.meta['item']
        for data in response.css('div.membership-directory--member--information '):
            url = data.css('a.btn::attr(href)').get()
            item = dict()
            item['Phone Number'] = data.css('p.phone-number::text').get('').strip()
            item['Email'] = data.css('p.email-address::text').get('').strip()
            yield scrapy.Request(url=url, meta={'item': item}, callback=self.detail_page, headers=self.headers)

        next_page = response.css('a[aria-label="Next Page"] i.next').get()
        if next_page:
            next_no = page_info.get('page') + 1
            page_info['page'] = next_no
            yield scrapy.Request(url=self.next.format(next_no), meta={'item': page_info},
                                 callback=self.parse, headers=self.headers)

    def detail_page(self, response):
        item = response.meta['item']
        item['Business Name'] = response.css('h1.title::text').get('').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('div.social-links a'))
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Georgiagrown Members'
        item['Source_URL'] = 'https://georgiagrown.com/membership/member-directory/'
        item['Lead_Source'] = 'georgiagrown'
        item['Business_Site'] = response.css(
            'div.gg_member_profile_single--description--company--info a.btn::text').get('').strip()
        yield item
