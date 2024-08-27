import scrapy


class NewsSpiderSpider(scrapy.Spider):
    name = 'news_spider'
    start_urls = ['https://www.news-gazette.com/marketplace/?action=srch']
    custom_settings = {
        'FEED_URI': 'news-gazette.csv',
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
        for data in response.css('ul.business-categories li a'):
            cate_url = data.css('::attr(href)').get()
            if cate_url:
                yield response.follow(url=cate_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.xpath('//div[@class="business-search-basic"]//div[@class="card-body"]'):
            detail_url = data.xpath('.//h4[@class="tnt-headline "]/a/@href').get()
            item = dict()
            item['Business Name'] = data.xpath('.//h4[@class="tnt-headline "]/a/text()').get('').strip()
            item['Phone Number'] = data.xpath('.//div[@class="card-phone"]/i/following-sibling::text()').get('').strip()
            if detail_url:
                yield response.follow(url=detail_url, callback=self.parse_detail,
                                      meta={'item': item}, headers=self.headers)
            else:
                item['Occupation'] = 'Business Service'
                item['Source_URL'] = 'https://www.news-gazette.com/marketplace/?action=srch'
                item['Lead_Source'] = 'news-gazette'
                item['Detail_Url'] = response.url
                yield item

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_listing, headers=self.headers)

    def parse_detail(self, response):
        item = response.meta['item']
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['State_Abrv'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Latitude'] = response.css('meta[itemprop="latitude"]::text').get('').strip()
        item['Longitude'] = response.css('meta[itemprop="longitude"]::text').get('').strip()
        item['Occupation'] = 'Business Service'
        item['Source_URL'] = 'https://www.news-gazette.com/marketplace/?action=srch'
        item['Lead_Source'] = 'news-gazette'
        item['Detail_Url'] = response.url
        yield item
