import scrapy


class AzlechamberSpiderSpider(scrapy.Spider):
    name = 'azlechamber_spider'
    request_api = 'https://business.azlechamber.com/list/searchalpha/{}'
    first_name = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                  'u',
                  'v', 'w', 'x', 'y', 'z']
    custom_settings = {
        'FEED_URI': 'azlechamber.csv',
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

    def start_requests(self):
        for first in self.first_name:
            yield scrapy.Request(url=self.request_api.format(first), callback=self.parse, headers=self.headers)

    def parse(self, response):
        for data in response.css('div.mn-listingcontent'):
            item = dict()
            item['Business Name'] = data.css('div[itemprop="name"] a::text').get('').strip()
            item['Detail_Url'] = data.css('div[itemprop="name"] a::attr(href)').get('').strip()
            item['Phone Number'] = data.css('li.mn-phone::text').get('').strip()
            item['Business_Site'] = data.css('li.mn-website a::attr(href)').get('').strip()
            item['Description'] = data.css('div[itemprop="description"]::text').get('').strip()
            item['Street Address'] = data.css('div[itemprop="streetAddress"]::text').get('').strip()
            item['State_Abrv'] = data.css('span[itemprop="addressRegion"]::text').get('').strip()
            item['Zip'] = data.css('span[itemprop="postalCode"]::text').get('').strip()
            item['Source_URL'] = 'https://business.azlechamber.com/list/searchalpha/a'
            item['Lead_Source'] = 'business.azlechamber'
            item['Occupation'] = 'Business Service'
            yield item
