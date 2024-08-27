import scrapy


class CollegedaletnSpiderSpider(scrapy.Spider):
    name = 'collegedaletn_spider'
    start_urls = ['https://www.collegedaletn.gov/community/business_directory.php']
    base_url = 'https://www.collegedaletn.gov/{}'
    custom_settings = {
        'FEED_URI': 'collegedaletn.csv',
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
        for data in response.css('div.rz-business-block'):
            item = dict()
            item['Business Name'] = data.css('h2::text').get('').strip()
            detail_url = data.css('a.rz-bus-readmore::attr(href)').get('').strip()
            if detail_url:
                item['Detail_Url'] = self.base_url.format(detail_url)
            item['Occupation'] = data.css('ul.category-list li::text').get('').strip()
            item['Phone Number'] = data.xpath('.//a/i[contains(@class,"fa-phone")]/following-sibling::text()').get('').strip()
            item['Street Address'] = data.xpath('.//a/i[contains(@class,"fa-map")]/following-sibling::text()').get('').strip()
            state = data.xpath('.//a/i[contains(@class,"fa-map")]/following-sibling::br/following-sibling::text()').get('').strip()
            if state:
                state_abb = state.split(',')[-1].strip()

                if state_abb:
                    item['State'] = state_abb.split('\xa')[0].strip()
                    item['Zip'] = state_abb.split('\xa')[-1].strip()
            item['Business_Site'] = data.xpath('.//a/i[contains(@class,"fa-globe")]/following-sibling::text()').get('').strip()
            item['Email'] = data.xpath('.//a/i[contains(@class,"fa-envelope")]/following-sibling::text()').get('').strip()
            item['Lead_Source'] = 'collegedaletn'
            item['Record_Type'] = 'Business'
            item['Source_URL'] = 'https://www.collegedaletn.gov/community/business_directory.php'
            yield item

