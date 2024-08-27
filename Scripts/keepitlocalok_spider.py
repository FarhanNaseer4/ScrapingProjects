import scrapy


class KeepitlocalokSpiderSpider(scrapy.Spider):
    name = 'keepitlocalok_spider'
    start_urls = ['https://www.keepitlocalok.com/members']
    base_url = 'https://www.keepitlocalok.com'
    url = 'https://www.keepitlocalok.com{}'
    custom_settings = {
        'FEED_URI': 'keepitlocalok.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('span.field-content a'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, headers=self.headers, dont_filter=True)
        next_page = response.css('li.pager-next a::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('div[id="slideshowBar"]::text').get('').strip()
        address = response.xpath('//div[@id="address"]/br/following-sibling::text()').get('').strip()
        if address:
            state = address.split(',')[-1].strip()
            if len(state.split(' ')) > 1:
                item['Zip'] = state.split(' ')[-1].strip()
                item['State_Abrv'] = state.split(' ')[0].strip()
        item['Street Address'] = response.xpath('//div[@id="address"]/div/following-sibling::text()').get('').strip()
        item['Phone Number'] = response.xpath('//div[@id="phone"]/div/following-sibling::text()').get('').strip()
        item['Email'] = response.css('div[id="email"] a::text').get('').strip()
        item['Business_Site'] = response.css('div[id="web"] a::attr(href)').get('').strip()
        item['Social_Media'] = ', '.join(link.css('::attr(href)').get() for link in response.css('div['
                                                                                                 'id="businessSocial'
                                                                                                 '"] a'))
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Business Service'
        item['Source_URL'] = 'https://www.keepitlocalok.com/members'
        item['Lead_Source'] = 'keepitlocalok'
        yield item


