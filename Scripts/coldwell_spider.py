import scrapy


class ColdwellSpiderSpider(scrapy.Spider):
    name = 'coldwell_spider'
    start_urls = ['https://www.coldwellbankerhomes.com/sitemap/agents/']
    base_url = 'https://www.coldwellbankerhomes.com{}'
    custom_settings = {
        'FEED_URI': 'coldwellbankerhomes.csv',
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

    def parse(self, response):
        for data in response.css('table.table-sort tr td:nth-child(1) a'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            yield scrapy.Request(url=state_url, callback=self.city_page, headers=self.headers)

    def city_page(self, response):
        for data in response.css('table.table-sort tr td:nth-child(1) a'):
            city_url = data.css('::attr(href)').get()
            if not city_url.startswith(self.base_url):
                city_url = self.base_url.format(city_url)
            yield scrapy.Request(url=city_url, callback=self.listing_page, headers=self.headers)

    def listing_page(self, response):
        for data in response.css('div.agent-block'):
            item = dict()
            fullname = data.css('h2[itemprop="name"] a::text').get('').strip()
            item['Full Name'] = fullname
            if fullname:
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = fullname.split(' ')[-1].strip()
            detail_url = data.css('h2[itemprop="name"] a::attr(href)').get()
            item['Phone Number 1'] = data.css('a[data-phone-type="mobile"]::text').get('').strip()
            item['Source_URL'] = 'https://www.coldwellbankerhomes.com/sitemap/agents/'
            item['Lead_Source'] = 'coldwellbankerhomes'
            item['Occupation'] = 'Agents'
            if detail_url:
                if not detail_url.startswith(self.base_url):
                    detail_url = self.base_url.format(detail_url)
                yield scrapy.Request(url=detail_url, meta={'item': item},
                                     callback=self.detail_page, headers=self.headers)
            else:
                yield item

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.listing_page, headers=self.headers)

    def detail_page(self, response):
        item = response.meta['item']
        item['Email'] = response.css('a.email-link::text').get('').strip()
        item['Phone Number'] = response.css('a[data-phone-type="office"]::text').get('').strip()
        address = response.css('ul.address-list li.notranslate span::text').get('').strip()
        if len(address.split(',')) > 1:
            item['Street Address'] = address.split(',')[0].strip()
            state = address.split(',')[-1].strip()
            if len(state.split(' ')) > 1:
                item['State_Abrv'] = state.split(' ')[0].strip()
                item['Zip'] = state.split(' ')[-1].strip()
        item['Detail_Url'] = response.url
        item['Business Name'] = response.css('ul.address-list li.notranslate a::text').get('').strip()
        yield item
