import scrapy


class PsychologytodaySpiderSpider(scrapy.Spider):
    name = 'psychologytoday_spider'
    start_urls = ['https://www.psychologytoday.com/us/therapists']
    zyte_key = '5871ec424f0a479ab721b3a757703580'
    custom_settings = {
        'CRAWLERA_ENABLED': True,
        'CRAWLERA_APIKEY': zyte_key,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy_crawlera.CrawleraMiddleware': 610
        },
        'HTTPERROR_ALLOW_ALL': True,
        'FEED_URI': 'psychologytoday.csv',
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
        for data in response.css('div.us_region_list ul.list-unstyled li a'):
            listing_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=listing_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div.results-row'):
            item = dict()
            item['Business Name'] = data.css('div.results-row-info a::text').get('').strip()
            detail_url = data.css('div.results-row-info a::attr(href)').get()
            item['Category'] = data.css('div.profile-subtitle::text').get('').strip()
            item['Description'] = data.css('div.statements::text').get('').strip()
            item['Phone Number'] = data.css('span.results-row-mob::text').get('').strip()
            if detail_url:
                yield scrapy.Request(url=detail_url, meta={'item': item},
                                     callback=self.detail_page, headers=self.headers)
            else:
                item[
                    'Source_URL'] = 'https://psychologytoday.com/us/therapists/fl/ponce-inlet?category=online' \
                                    '-counseling '
                item['Lead_Source'] = 'psychologytoday'
                item['Occupation'] = 'Therapists'
                yield item
        next_page = response.xpath('//a[contains(@title,"Next Therapists")]/@href').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.listing_page, headers=self.headers)

    def detail_page(self, response):
        item = response.meta['item']
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['State_Abrv'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalcode"]::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://psychologytoday.com/us/therapists/fl/ponce-inlet?category=online-counseling'
        item['Lead_Source'] = 'psychologytoday'
        item['Occupation'] = 'Therapists'
        yield item
