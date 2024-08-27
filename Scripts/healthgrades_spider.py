import scrapy


class HealthgradesSpiderSpider(scrapy.Spider):
    name = 'healthgrades_spider'
    start_urls = ['https://www.healthgrades.com/specialty-directory']
    base_url = 'https://www.healthgrades.com{}'
    custom_settings = {
        'FEED_URI': 'healthgrades.csv',
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
        'authority': 'www.healthgrades.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('li.listArray__name a'):
            url = data.css('::attr(href)').get()
            if not url.startswith(self.base_url):
                url = self.base_url.format(url)
            yield scrapy.Request(url=url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.results-card-info__primary-info h3 a'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        fullname = response.css('div h1::text').get('').strip()
        if len(fullname.split(',')) > 1:
            name = fullname.split(',')[0].strip()
            item['Full Name'] = name
            if len(name.split(' ')) > 2:
                item['First Name'] = name.split(' ')[0].strip()
                item['Last Name'] = name.split(' ')[2].strip()
            else:
                item['First Name'] = name.split(' ')[0].strip()
                item['Last Name'] = name.split(' ')[1].strip()
        else:
            item['Full Name'] = fullname
        item['Description'] = response.css('p.auto-bio-clamped-three::text').get('').strip()
        item['Business Name'] = response.css('p.location-practice::text').get('').strip()
        phone = response.css('a[data-qa-target="toggle-phone-number-office-phone"]::text').get()
        if phone:
            item['Phone Number'] = phone.strip()
        else:
            item['Phone Number'] = response.css('a[data-qa-target="pdc-summary-new-patients-button"]::text').get('').strip()
        item['Reviews'] = response.css('div.overall-rating strong::text').get('').strip()
        item['Street Address'] = response.css('span.street-address::text').get('').strip()
        state = response.css('address.address span span:nth-child(2)::text').get()
        if state:
            item['State'] = state.strip()
            item['State_Abrv'] = response.css('address.address span span:nth-child(3)::text').get('').strip()
            item['Zip'] = response.css('address.address span span:nth-child(4)::text').get('').strip()
        else:
            item['State'] = response.css('address.address div span:nth-child(3)::text').get('').strip()
            item['State_Abrv'] = response.css('address.address div span:nth-child(4)::text').get('').strip()
            item['Zip'] = response.css('address.address div span:nth-child(5)::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://healthgrades.com/group-directory/il-illinois/hanover-park/beautiful-mind' \
                             '-therapy-oovcm6c '
        item['Occupation'] = 'Doctors'
        item['Lead_Source'] = 'healthgrades'
        yield item

