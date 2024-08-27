import scrapy


class LawyersSpiderSpider(scrapy.Spider):
    name = 'lawyers_spider'
    start_urls = ['https://lawyers.oyez.org/lawyers/indiana/']
    base_url = 'https://lawyers.oyez.org{}'
    custom_settings = {
        'FEED_URI': 'lawyers_oyez.csv',
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
        'Accept-Language': 'en-US,en;q=0.9',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    }

    def parse(self, response):
        for data in response.css('a.main-profile-link'):
            detail_url = data.css('::attr(href)').get()
            if not detail_url.startswith(self.base_url):
                detail_url = self.base_url.format(detail_url)
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

        next_page = response.css('span.next a::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('span.small-font::text').get('').strip()
        fullname = response.css('h1.lawyer-name::text').get('').strip()
        item['Full Name'] = fullname
        if len(fullname.split(' ')) > 2:
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[2].strip()
        else:
            if len(fullname.split(' ')) > 1:
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = fullname.split(' ')[1].strip()
            else:
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = ''
        item['Business_Site'] = response.css('a[aria-label="Website 1"]::attr(href)').get('').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('div.-social-badges a'))
        item['Street Address'] = response.css('div.street-address::text').get('').strip()
        item['State'] = response.css('span.locality::text').get('').strip()
        item['State_Abrv'] = response.css('span.region::text').get('').strip()
        item['Zip'] = response.css('span.postal-code::text').get('').strip()
        item['Phone Number'] = response.css('span.value span::text').get('').strip()
        item['Occupation'] = 'lawyer'
        item['Source_URL'] = 'https://lawyers.oyez.org/lawyers/indiana/richmond'
        item['Lead_Source'] = 'lawyers.oyez'
        item['Detail_Url'] = response.url
        yield item
