import scrapy


class HomelendingadvisorSpiderSpider(scrapy.Spider):
    name = 'homelendingadvisor_spider'
    start_urls = ['https://homelendingadvisor.chase.com/']

    custom_settings = {
        'FEED_URI': 'homelendingadvisor.csv',
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
        for data in response.css('a.Directory-listLink'):
            state_url = data.css('::attr(href)').get()
            if len(state_url.split('/')) > 1:
                yield response.follow(url=state_url, callback=self.parse_detail, headers=self.headers)
            else:
                yield response.follow(url=state_url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('a.Directory-listLink'):
            list_url = data.css('::attr(href)').get()
            if len(list_url.split('/')) > 2:
                yield response.follow(url=list_url, callback=self.parse_detail, headers=self.headers)
            else:
                yield response.follow(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('a.Teaser-titleLink'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        fullname = response.css('h1[itemprop="name"]::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Phone Number'] = response.css('div[itemprop="telephone"]::text').get('').strip()
        item['Street Address'] = response.css('span.c-address-street-1::text').get('').strip()
        item['State'] = response.css('abbr.c-address-state::text').get('').strip()
        item['Zip'] = response.css('span.c-address-postal-code::text').get('').strip()
        item['Email'] = response.xpath('//div[@class="Core-email"]/text()').get('').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = response.css('div.Core-titlePosition::text').get('').strip()
        item['Lead_Source'] = 'homelendingadvisor'
        item['Record_Type'] = 'Person'
        item['Source_URL'] = 'https://homelendingadvisor.chase.com/'
        yield item
