import scrapy


class FinduslocalScrapperSpider(scrapy.Spider):
    name = 'finduslocal_scrapper'
    start_urls = ['https://www.finduslocal.com/health-services']
    custom_settings = {
        'FEED_URI': 'finduslocal_data.csv',
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
        'authority': 'www.finduslocal.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.post'):
            item = dict()
            detail_url = data.css('div.left h2 a::attr(href)').get('')
            item['Business Name'] = data.css('div.left h2 a::text').get('').strip()
            item['Occupation'] = data.css('div.left h3::text').get('').strip()
            item['Street Address'] = data.css('span[itemprop="streetAddress"]::text').get('').strip()
            item['State_Abrv'] = data.css('span[itemprop="addressRegion"]::text').get('').strip()
            item['Zip'] = data.css('span[itemprop="postalCode"]::text').get('').strip()
            yield scrapy.Request(url=detail_url, meta={'item': item}, callback=self.parse_data, headers=self.headers)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)

    def parse_data(self, response):
        item = response.meta['item']
        item['Phone Number'] = response.css('h1.custom_h1 a.mr-1::text').get('').strip()
        item['Description'] = response.css('div.col-sm-12 p::text').get('').strip()
        item['Full Name'] = response.xpath('//div[@id="rightOfPhoto"]/a[not(@class)]/text()').get('').strip()
        item['Source_URL'] = 'https://www.finduslocal.com/health-services'
        item['Lead_Source'] = 'finduslocal'
        item['Reviews'] = response.xpath('//div[not(@class)]/a/span[@class="iprop"]/text()').get('').strip()
        item['Rating'] = response.xpath('//div[not(@class)]/span[@class="iprop"]/text()').get('').strip()
        yield item