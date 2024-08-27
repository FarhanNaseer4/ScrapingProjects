import scrapy


class GreenamericaSpiderSpider(scrapy.Spider):
    name = 'greenamerica_spider'
    start_urls = ['https://greenamerica.org/all-directory-listings-breakupwithyourbank?title=a'
                  '&field_directory_list_address_locality=']
    custom_settings = {
        'FEED_URI': 'greenamerica.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']
    }

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('table.table-striped tr td.views-field-title a'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.css('a[rel="next"]::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.page-header span::text').get('').strip()
        item['Category'] = response.css('div.field--name-field-listing-type a::text').get('').strip()
        item['Phone Number'] = response.css('div.field--name-field-telephone a::text').get('').strip()
        item['Business_Site'] = response.css('div.field--name-field-website a::text').get('').strip()
        item['Latitude'] = response.css('div.geolocation-location::attr(data-lat)').get('').strip()
        item['Longitude'] = response.css('div.geolocation-location::attr(data-lng)').get('').strip()
        item['Source_URL'] = 'https://greenamerica.org/all-directory-listings-breakupwithyourbank?title=a' \
                             '&field_directory_list_address_locality= '
        item['Occupation'] = 'Business Service'
        item['Lead_Source'] = 'greenamerica'
        item['Record_Type'] = 'Business'
        item['Detail_Url'] = response.url
        yield item



