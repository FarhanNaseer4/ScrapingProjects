import scrapy


class NweconSpiderSpider(scrapy.Spider):
    name = 'nwecon_spider'
    start_urls = ['https://www.nwecon.org/']
    base_url = 'https://www.nwecon.org{}'
    custom_settings = {
        'FEED_URI': 'nwecon.csv',
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
        for data in response.xpath('//div[@class="right"]//h3[contains(text(),"Category")]/following-sibling::ul/li/a'):
            comp_url = data.xpath('./@href').get()
            yield response.follow(url=comp_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.vcard'):
            item = dict()
            item['Business Name'] = data.css('span.org a::text').get('').strip()

            item['Street Address'] = data.css('span.street-address::text').get('').strip()
            item['State_Abrv'] = data.css('span.region::text').get('').strip()
            item['Zip'] = data.css('span.postal-code::text').get('').strip()
            item['Latitude'] = data.css('span.latitude span::attr(title)').get('').strip()
            item['Longitude'] = data.css('span.longitude span::attr(title)').get('').strip()
            item['Phone Number'] = data.xpath('.//span[@class="tel"]/text()').get('').strip()
            item['Detail_Url'] = self.base_url.format(data.css('span.org a::attr(href)').get('').strip())
            item['Occupation'] = 'Stores'
            item['Source_URL'] = 'https://nwecon.org/welding/Old-Appleton-MO-city/directory.html'
            item['Lead_Source'] = 'nwecon'
            yield item

