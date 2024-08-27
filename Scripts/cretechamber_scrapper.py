import scrapy


class CretechamberScrapperSpider(scrapy.Spider):
    name = 'cretechamber_scrapper'
    start_urls = ['https://www.cretechamber.org/list/search?c=25&q=&st=1']
    request_url = 'https://www.cretechamber.org/list/search?c={}&q=&st=1'
    first_name = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    headers = {
        'authority': 'www.cretechamber.org',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }
    custom_settings = {
        'FEED_URI': 'cretechamber_data.csv',
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

    def parse(self, response):
        for data in response.xpath('//select[@class="mn-form-dropdown"]//following::option'):
            c = data.xpath('./@value').get()
            item = dict()
            item['Occupation'] = data.xpath('./text()').get('').strip()
            yield scrapy.Request(url=self.request_url.format(c), meta={'item': item},
                                 callback=self.parse_data, headers=self.headers)

    def parse_data(self, response):
        item = response.meta['item']
        for data in response.css('div.mn-listing div.mn-listingcontent'):
            item['Business Name'] = data.css('div[itemprop="name"] a::text').get('').strip()
            item['Detail_Url'] = data.css('div[itemprop="name"] a::attr(href)').get('').strip()
            item['Street Address'] = data.css('div[itemprop="streetAddress"]::text').get('').strip()
            item['State_Abrv'] = data.css('span[itemprop="addressRegion"]::text').get('').strip()
            item['Zip'] = data.css('span[itemprop="postalCode"]::text').get('').strip()
            item['Phone Number'] = data.css('li.mn-phone::text').get('').strip()
            item['Source_URL'] = 'https://www.cretechamber.org/'
            item['Lead_Source'] = 'cretechamber'
            yield item



