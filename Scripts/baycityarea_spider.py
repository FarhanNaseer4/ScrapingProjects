import scrapy


class BaycityareaSpiderSpider(scrapy.Spider):
    name = 'baycityarea_spider'
    start_urls = ['https://www.baycityarea.com/list']
    custom_settings = {
        'FEED_URI': 'baycityarea.csv',
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
        'authority': 'www.baycityarea.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_ga=GA1.2.355305373.1663578622; _gid=GA1.2.1774134057.1663578622; _gat=1',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }

    def parse(self, response):
        for data in response.css('div.gz-alphanumeric-btn a'):
            url = data.css('::attr(href)').get()
            yield scrapy.Request(url=url, callback=self.parse_data, headers=self.headers)

    def parse_data(self, response):
        for data in response.css('div.card-header a'):
            url = data.css('::attr(href)').get()
            yield scrapy.Request(url=url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.gz-pagetitle::text').get('').strip()
        item['Occupation'] = response.css('div.gz-details-categories p span:nth-child(1)::text').get('').strip()
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['State'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Phone Number'] = response.css('span[itemprop="telephone"]::text').get('').strip()
        item['Business_Site'] = response.css('li.gz-card-website span[itemprop="sameAs"]::text').get('').strip()
        item['Social Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('li.gz-card-social a'))
        item['Description'] = response.css('div[itemprop="description"] p::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://baycityarea.com/list'
        item['Lead_Source'] = 'baycityarea'
        yield item

