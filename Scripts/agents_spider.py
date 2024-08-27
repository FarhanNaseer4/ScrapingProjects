import scrapy


class AgentsSpiderSpider(scrapy.Spider):
    name = 'agents_spider'
    start_urls = ['https://agents.farmers.com/index.html']
    base_url = 'https://agents.farmers.com/{}'
    custom_settings = {
        'FEED_URI': 'agents_farmer.csv',
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
        'authority': 'agents.farmers.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('a.Directory-listLink'):
            state_url = data.css('::attr(href)').get()
            if not state_url.startswith(self.base_url):
                state_url = self.base_url.format(state_url)
            if 'karen-carey' in state_url:
                yield scrapy.Request(url=state_url, callback=self.detail_page, headers=self.headers)
            else:
                yield scrapy.Request(url=state_url, callback=self.get_city_data, headers=self.headers)

    def get_city_data(self, response):
        for data in response.css('a.Directory-listLink'):
            city_url = data.css("::attr(href)").get()
            if not city_url.startswith(self.base_url):
                city_url = self.base_url.format(city_url)
            if len(city_url.split('/')) == 6:
                yield scrapy.Request(url=city_url, callback=self.detail_page, headers=self.headers)
            else:
                yield scrapy.Request(url=city_url, callback=self.get_listing, headers=self.headers)

    def get_listing(self, response):
        for data in response.css('div.Teaser-topSection a.Teaser-title-link'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        fullname = response.css('h1[itemprop="name"]::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Street Address'] = response.css('div[itemprop="location"] span.c-address-street-1::text').get('').strip()
        item['State_Abrv'] = response.css('div[itemprop="location"] abbr[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('div[itemprop="location"] span[itemprop="postalCode"]::text').get('').strip()
        item['Phone Number'] = response.css('div[id="phone-main"]::text').get('').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get()for data in response.css('div.SocialIcon'
                                                                                                '-wrapper a'))
        item['Occupation'] = 'Insurance Agent'
        item['Source_URL'] = 'https://agents.farmers.com/ks/mound-city'
        item['Lead_Source'] = 'agents.farmers'
        item['Detail_Url'] = response.url
        yield item

