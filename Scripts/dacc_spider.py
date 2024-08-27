import scrapy


class DaccSpiderSpider(scrapy.Spider):
    name = 'dacc_spider'
    start_urls = ['https://dacc.edu/directory']
    custom_settings = {
        'FEED_URI': 'dacc.csv',
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
        for data in response.xpath('//a[contains(@href,"surname")]'):
            url = data.xpath('./@href').get()
            if url:
                yield response.follow(url=url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('table.directory tr'):
            item = dict()
            if data.css('td:nth-child(1)'):
                full_name = data.css('td:nth-child(1)::text').get('').strip()
                if full_name:
                    item['Last Name'] = full_name.split(',')[0].strip()
                    item['First Name'] = full_name.split(',')[-1].strip()
                    item['Full Name'] = item['First Name'] + ' ' + item['Last Name']
                item['Email'] = data.css('td:nth-child(2) a::text').get('').strip()
                item['Phone Number'] = data.css('td:nth-child(3)::text').get('').strip()
                item['Business Name'] = data.css('td:nth-child(4)::text').get('').strip()
                item['Occupation'] = data.css('td:nth-child(5)::text').get('').strip()
                item['Source_URL'] = 'https://dacc.edu/directory'
                item['Lead_Source'] = 'dacc'
                yield item

