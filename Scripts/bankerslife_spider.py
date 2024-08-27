import scrapy


class BankerslifeSpiderSpider(scrapy.Spider):
    name = 'bankerslife_spider'
    start_urls = ['https://agents.bankerslife.com/index.html']
    custom_settings = {
        'FEED_URI': 'agents_bankerslife.csv',
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('a.Directory-listLink'):
            url = data.css('::attr(href)').get()
            yield response.follow(url=url, callback=self.parse_city, headers=self.headers)

    def parse_city(self, response):
        if response.css('a.Directory-listLink'):
            for data in response.css('a.Directory-listLink'):
                list_url = data.css('::attr(href)').get()
                yield response.follow(url=list_url, callback=self.parse_listing, headers=self.headers)
        else:
            if response.css('a.Teaser-titleLink'):
                for data in response.css('a.Teaser-titleLink'):
                    detail_url = data.css('::attr(href)').get()
                    yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('a.Teaser-titleLink'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        fullname = response.css('h1.Hero-titleText::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Business_Site'] = response.css('ul.mt-6 a.flex-1::attr(href)').get('').strip()
        item['Email'] = response.css('a.Core-email::text').get('').strip()
        item['Phone Number'] = response.css('span[itemprop="telephone"]::text').get('').strip()
        item['Phone Number 1'] = response.css('span.c-phone-alternate-number-span::text').get('').strip()
        item['Street Address'] = response.css('span.c-address-street-1::text').get('').strip()
        item['State'] = response.css('abbr.c-address-state::text').get('').strip()
        item['Zip'] = response.css('span.c-address-postal-code::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://agents.bankerslife.com/index.html'
        item['Lead_Source'] = 'agents.bankerslife'
        item['Occupation'] = response.css('div.Hero-agentTitle::text').get('').strip()
        item['Record_Type'] = 'Person'
        yield item
