import scrapy


class AtlantamagazineSpiderSpider(scrapy.Spider):
    name = 'atlantamagazine_spider'
    start_urls = ['https://www.atlantamagazine.com/top-doctors/']
    custom_settings = {
        'FEED_URI': 'atlantamagazine.csv',
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
        'authority': 'www.atlantamagazine.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('div.specialtyList a'):
            doc_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=doc_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.docListing'):
            item = dict()
            full_name = data.css('p.docName::text').get('').strip()
            if len(full_name.split(',')) > 1:
                item['Full Name'] = full_name.split(',')[0].strip()
                name = full_name.split(',')[0].strip()
                if len(name.split(' ')) > 2:
                    item['First Name'] = name.split(' ')[0].strip()
                    item['Last Name'] = name.split(' ')[2].strip()
                else:
                    item['First Name'] = name.split(' ')[0].strip()
                    item['Last Name'] = name.split(' ')[1].strip()
            else:
                item['Full Name'] = full_name.strip()
            item['Business Name'] = data.css('p.docHospital::text').get('').strip()
            street_address = data.xpath('//p[@class="contactInfo"]/text()').get('').strip()
            if len(street_address.split(',')) >= 3:
                item['Street Address'] = street_address.split(',')[0].strip()
                state_data = street_address.split(',')[-1].strip()
                if len(state_data.split(' ')) > 1:
                    item['State_Abrv'] = state_data.split(' ')[0].strip()
                    item['Zip'] = state_data.split(' ')[1].strip()
            else:
                if len(street_address.split(',')) <= 2:
                    item['Street Address'] = street_address.split(',')[0].strip()
                    state_data = street_address.split(',')[2].strip()
                    if len(state_data.split(' ')) > 1:
                        item['State_Abrv'] = state_data.split(' ')[0].strip()
                        item['Zip'] = state_data.split(' ')[1].strip()
            item['Phone Number'] = data.xpath('//p[@class="contactInfo"]/br/following::text()').get('').strip()
            item['Occupation'] = response.css('h2.specialtyHeaders::text').get('').strip()
            item['Source_URL'] = 'https://www.atlantamagazine.com/top-doctors/'
            item['Lead_Source'] = 'atlantamagazine'
            yield item
