import scrapy


class GabarSpiderSpider(scrapy.Spider):
    name = 'gabar_spider'
    start_urls = ['https://gabar.org/membersearchresults.cfm']
    custom_settings = {
        'FEED_URI': 'gabar.csv',
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('div.member-name a'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

        next_page = response.css('a[aria-label="Next"]::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        fullname = response.css('div.course-id h3::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[1].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Email'] = response.xpath('//a[contains(@href,"mailto")]/text()').get('').strip()
        item['Phone Number'] = response.xpath('//p/strong[contains(text(),"Phone")]/following::td/text()').get('').strip()
        street_address = response.xpath('//div[@class="course-box"]/p/br/following-sibling::text()').get('').strip()
        if len(street_address.split(',')) == 3:
            if street_address:
                if len(street_address.split(',')) > 1:
                    state = street_address.split(',')[1].strip()
                    if state:
                        item['State'] = state.split(' ')[0].strip()
                        item['Zip'] = state.split(' ')[-1].strip()
        else:
            item['Street Address'] = street_address
            state_data = response.xpath('//div[@class="course-box"]/p/br/following-sibling::br/following-sibling::text()').get('').strip()
            if state_data:
                if len(state_data.split(',')) > 1:
                    state = state_data.split(',')[1].strip()
                    if state:
                        item['State'] = state.split(' ')[0].strip()
                        item['Zip'] = state.split(' ')[-1].strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://gabar.org/membersearchresults.cfm'
        item['Lead_Source'] = 'gabar'
        item['Occupation'] = 'Lawyer'
        item['Record_Type'] = 'Person'
        yield item
