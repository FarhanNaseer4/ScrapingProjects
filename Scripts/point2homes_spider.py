import scrapy


class Point2homesSpiderSpider(scrapy.Spider):
    name = 'point2homes_spider'
    start_urls = ['https://www.point2homes.com/US/Real-Estate-Agents.html']

    custom_settings = {
        'FEED_URI': 'point2homes.csv',
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
        for data in response.css('div.outer-column div a'):
            list_url = data.css('::attr(href)').get()
            yield response.follow(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('ul.agent-links a.ic-profile'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

        next_page = response.css('a.pager-next::attr(href)').get()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse_listing, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        fullname = response.css('h1.agent-name span::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        address = response.xpath('//div[@class="agent-location"]//text()').get('').strip()
        if address:
            item['Street Address'] = address.split(',')[0].strip()
            state = address.split(',')[-1].strip()
            if len(state.split(' ')) > 1:
                item['State'] = state.split(' ')[0].strip()
                item['Zip'] = state.split(' ')[-1].strip()
        item['Phone Number'] = response.css('li.phone-cell span.ic-phone::attr(data-phone)').get('').strip()
        item['Phone Number 1'] = response.css('li.phone-office span.ic-phone::attr(data-phone)').get('').strip()
        item['Business_Site'] = response.css('div.website a::attr(href)').get('').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('div.social-button-cnt a'))
        item['Source_URL'] = 'https://www.point2homes.com/US/Real-Estate-Agents.html'
        item['Occupation'] = 'Agent'
        item['Lead_Source'] = 'point2homes'
        item['Record_Type'] = 'Person'
        item['Detail_Url'] = response.url
        yield item
