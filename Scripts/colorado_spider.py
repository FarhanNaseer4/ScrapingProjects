import scrapy


class ColoradoSpiderSpider(scrapy.Spider):
    name = 'colorado_spider'
    start_urls = ['https://www.colorado.com/visitor-directory']
    base_url = 'https://www.colorado.com{}'
    custom_settings = {
        'FEED_URI': 'colorado_visitor.csv',
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
        for data in response.css('div.views-row div.field__item h3 a'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('div.field__item h1::text').get('').strip()
        item['Street Address'] = response.css('div.address::text').get('').strip()
        item['State_Abrv'] = response.css('span.state::text').get('').strip()
        item['Zip'] = response.css('span.zip::text').get('').strip()
        item['Occupation'] = 'HOTELS & LODGING'
        item['Phone Number'] = response.css('a[data-action="outbound_full--local-phone"]::text').get('').strip()
        item['Phone Number 1'] = response.css('a[data-action="outbound_full--tollfree-phone"]::text').get('').strip()
        item['Business_Site'] = response.css('a.website-link::attr(href)').get('').strip()
        item['Source_URL'] = 'https://colorado.com/visitor-directory'
        item['Lead_Source'] = 'colorado'
        item['Detail_Url'] = response.url
        yield item
