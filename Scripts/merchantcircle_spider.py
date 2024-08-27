import scrapy


class MerchantcircleSpiderSpider(scrapy.Spider):
    name = 'merchantcircle_spider'
    start_url = 'https://www.merchantcircle.com/ut-riverton/professional-services'
    next_url = 'https://www.merchantcircle.com/ut-riverton/professional-services?start={}#hubResults'
    custom_settings = {
        'FEED_URI': 'merchantcircle.csv',
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
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    }

    def start_requests(self):
        item = {'next_page': 2,
                'offset': 0}
        yield scrapy.Request(url=self.start_url, meta={'item': item}, callback=self.parse, headers=self.headers)

    def parse(self, response):
        item = response.meta['item']
        for data in response.css('div.vcard a.url'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, meta={'item': item}, callback=self.detail_page, headers=self.headers)
        next_page = response.css('div.pagination a:nth-child(8)::attr(href)').get()
        total_pages = 477
        next_page = item.get('next_page')
        offset = item.get('offset')
        if next_page < total_pages:
            item['next_page'] = next_page + 1
            offset = offset + 15
            item['offset'] = offset
            yield scrapy.Request(url=self.next_url.format(offset), meta={'item': item},
                                 callback=self.parse, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('h1[itemprop="name"]::text').get('').strip()
        item['Phone Number'] = response.css('span[itemprop="telephone"]::text').get('').strip()
        item['Street Address'] = response.css('span.address-line-1::text').get('').strip()
        item['State_Abrv'] = response.css('span[id="business-state"]::text').get('').strip()
        item['Zip'] = response.css('span[id="business-zipcode"]::text').get('').strip()
        item['Reviews'] = response.css('span[id="business-review-count"]::text').get('').strip()
        item['Rating'] = response.css('label[id="business-aggregate-rating"]::text').get('').strip()
        item['Description'] = response.css('p[id="business-description"]::text').get('').strip()
        item['Source_URL'] = 'https://merchantcircle.com/ut-riverton/professional-services'
        item['Lead_Source'] = 'merchantcircle'
        item['Detail_Url'] = response.url
        yield item
