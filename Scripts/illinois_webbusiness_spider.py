import scrapy


class IllinoisWebbusinessSpiderSpider(scrapy.Spider):
    name = 'illinois-webbusiness_spider'
    start_urls = ['https://illinois-webbusiness.com/']
    base_url = 'https://illinois-webbusiness.com/{}'
    custom_settings = {
        'FEED_URI': 'illinois-webbusiness.csv',
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('div.content-link-search a'):
            cate_url = data.css('::attr(href)').get()
            if cate_url:
                yield response.follow(url=cate_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.ent_container'):
            detail_url = data.xpath('.//div[@class="info-map-top"]/a/@href').get()
            if detail_url:
                yield scrapy.Request(url=self.base_url.format(detail_url), callback=self.parse_detail, headers=self.headers)

        next_page = response.xpath('//span[@class="pages"]/a[contains(text(),"next")]/@href').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_listing, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Street Address'] = response.xpath('//td[contains(text(),"Address")]/strong/text()').get('').strip()
        item['Zip'] = response.xpath('//td[contains(text(),"Zip")]/strong/text()').get('').strip()
        item['Phone Number'] = response.xpath('//td[contains(text(),"Phone")]/strong/text()').get('').replace('\xad', '').strip()
        item['Business_Site'] = response.xpath('//td/a[contains(text(),"Website")]/text()').get('').strip()
        item['Business Name'] = response.css('h1.org::text').get('').strip()
        item['Category'] = response.xpath('//td[contains(text(),"Type")]/b/text()').get('').strip()
        item['Source_URL'] = 'https://illinois-webbusiness.com/search.php?q=health&e=surgeon&city=roodhouse'
        item['Lead_Source'] = 'illinois-webbusiness'
        item['Occupation'] = 'Business Service'
        item['Detail_Url'] = response.url
        yield item

