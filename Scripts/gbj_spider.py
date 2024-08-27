import scrapy


class GbjSpiderSpider(scrapy.Spider):
    name = 'gbj_spider'
    start_urls = ['https://gbj.com/categories']
    base_url = 'https://gbj.com{}'
    custom_settings = {
        'FEED_URI': 'gbj.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation'],
    }
    headers = {
        'authority': 'gbj.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('a.sub-category'):
            listing_url = data.css('::attr(href)').get()
            if not listing_url.startswith(self.base_url):
                listing_url = self.base_url.format(listing_url)
            yield scrapy.Request(url=listing_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.grid_element a.center-block'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('span.textbox-company::text').get('').strip()
        item['Business_Site'] = response.css('a[title="website"]::attr(href)').get()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('li'
                                                                                                 '.member_social_icons a'))
        item['Street Address'] = response.xpath(
            '//li[contains(text(), "Location")]/following-sibling::li/span/text()').get('').strip()
        zipc = response.xpath(
            '//li[contains(text(), "Location")]/following-sibling::li//br/following-sibling::span/following-sibling'
            '::span/following-sibling::span/text()').get().strip()
        if zipc:
            item['Zip'] = zipc.strip()
        phone = response.xpath('//li[contains(text(), "Phone Number")]/following-sibling::li/text()').get()
        if phone:
            item['Phone Number'] = phone.strip()
        item['Description'] = response.css('div#div1 p span::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = response.css('span.profile-header-top-category::text').get('').strip()
        item['Source_URL'] = 'https://gbj.com/lilburn/shopping/funeral-homes'
        item['Lead_Source'] = 'gbj'
        yield item
