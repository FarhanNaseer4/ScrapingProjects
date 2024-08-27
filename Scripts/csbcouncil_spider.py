import scrapy


class CsbcouncilSpiderSpider(scrapy.Spider):
    name = 'csbcouncil_spider'
    start_urls = ['https://www.csbcouncil.org/local/']
    base_url = 'https://www.csbcouncil.org{}'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    custom_settings = {
        'FEED_URI': 'csbcouncil.csv',
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

    def parse(self, response):
        for data in response.css('div.left-box ul li a'):
            sub_cate_url = data.css('::attr(href)').get()
            if not sub_cate_url.startswith(self.base_url):
                sub_cate_url = self.base_url.format(sub_cate_url)
            yield scrapy.Request(url=sub_cate_url, callback=self.get_sub_category, headers=self.headers)

    def get_sub_category(self, response):
        for data in response.css('div.sublist a'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            yield scrapy.Request(url=state_url, callback=self.get_state_url, headers=self.headers)

    def get_state_url(self, response):
        for data in response.xpath('//h3[contains(text()," By State")]/following-sibling::div/div//li/a'):
            list_url = data.xpath('./@href').get()
            if not list_url.startswith(self.base_url):
                list_url = self.base_url.format(list_url)
            yield scrapy.Request(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.vcard'):
            detail_url = data.css('span.org a::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.xpath('//a[contains(text(),">")]/@href').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse_listing, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('span.org::text').get('').strip()
        item['Business_Site'] = response.css('span.url a::attr(href)').get()
        item['Street Address'] = response.css('span.street-address::text').get('').strip()
        item['State_Abrv'] = response.css('span.region::text').get('').strip()
        item['Zip'] = response.css('span.postal-code::text').get('').strip()
        item['Phone Number'] = response.xpath('//span[@class="tel"]/text()').get('').strip()
        item['Latitude'] = response.css('span.latitude span::attr(title)').get('').strip()
        item['Longitude'] = response.css('span.longitude span::attr(title)').get('').strip()
        item['Business_Type'] = response.css('div.company-box h2::text').get('').strip()
        item['Occupation'] = 'Business Service'
        item['Source_URL'] = 'https://www.csbcouncil.org/local/'
        item['Lead_Source'] = 'csbcouncil'
        yield item
