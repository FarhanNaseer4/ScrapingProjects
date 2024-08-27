import scrapy


class GalvnewsSpiderSpider(scrapy.Spider):
    name = 'galvnews_spider'
    start_urls = ['https://www.galvnews.com/businessdirectory/']
    base_url = 'https://www.galvnews.com{}'
    custom_settings = {
        'FEED_URI': 'galvnews.csv',
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
        'Accept': 'application/json',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('div.list-group-item h4 a'):
            list_url = data.css('::attr(href)').get()
            yield response.follow(url=list_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div.business-search-basic div.card-body'):
            detail_url = data.css('h4.tnt-headline a::attr(href)').get('').strip()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(url=self.base_url.format(next_page), callback=self.listing_page,
                                  headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('h1[itemprop="name"]::text').get('').strip()
        item['Phone Number'] = response.css('span[itemprop="telephone"]::text').get('').strip()
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['State_Abrv'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Category'] = ', '.join(cate.css('::text').get() for cate in response.css('div.business-categories ul.list-unstyled li a'))
        item['Occupation'] = response.css('div.block-title-inner h3 a::text').get('').strip()
        item['Source_URL'] = 'https://galvnews.com/obituaries/article_2705d51e-fc80-11e3-9a4b-0017a43b2370.html'
        item['Lead_Source'] = 'galvnews'
        yield item
