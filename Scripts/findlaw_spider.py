import scrapy


class FindlawSpiderSpider(scrapy.Spider):
    name = 'findlaw_spider'
    start_urls = ['https://lawyers.findlaw.com/lawyer/statepractice/new-york/new-york']
    base_url = 'https://lawyers.findlaw.com{}'
    details = 'https:'
    detail_base = 'https:{}'
    custom_settings = {
        'FEED_URI': 'findlaw.csv',
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
        'authority': 'lawyers.findlaw.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('li.li-adjust a'):
            listing_url = data.css('::attr(href)').get()
            if not listing_url.startswith(self.base_url):
                listing_url = self.base_url.format(listing_url)
            yield scrapy.Request(url=listing_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div[id="standard_results"] li div.name-and-desc a'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.details):
                detail_url = self.detail_base.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse_listing, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.listing-details-header::text').get('').strip()
        item['Street Address'] = response.css('p.pp_card_street span:nth-child(1)::text').get('').strip()
        item['Zip'] = response.css('p.pp_card_street span:nth-child(5)::text').get('').strip()
        item['Phone Number'] = response.css('a.profile-phone-header::attr(href)').get('').replace('tel:', '').strip()
        item['Business_Site'] = response.css('a.profile-website-header::attr(href)').get('').strip()
        item['Description'] = response.css('div[id="pp_overview_text"] p::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://caselaw.findlaw.com/us-7th-circuit/1586667.html'
        item['Occupation'] = 'Law Firms'
        item['Lead_Source'] = 'caselaw.findlaw'
        yield item

