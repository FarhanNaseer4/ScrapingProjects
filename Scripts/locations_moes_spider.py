import scrapy


class LocationsMoesSpiderSpider(scrapy.Spider):
    name = 'locations_moes_spider'
    start_urls = ['https://locations.moes.com/?_ga=2.224011803.1605964465.1665741463-51603040.1665741463']
    custom_settings = {
        'FEED_URI': 'locations_moes.csv',
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
        for data in response.css('a.Directory-listLink'):
            state_url = data.css('::attr(href)').get()

            if len(state_url.split('/')) == 1:
                yield response.follow(url=state_url, callback=self.parse_city, headers=self.headers)
            else:
                yield response.follow(url=state_url, callback=self.parse_detail, headers=self.headers)

    def parse_city(self, response):
        for data in response.css('a.Directory-listLink'):
            city_url = data.css('::attr(href)').get()
            # print(len(city_url.split('/')))
            if len(city_url.split('/')) == 2:
                yield response.follow(url=city_url, callback=self.parse_listing, headers=self.headers)
            else:
                yield response.follow(url=city_url, callback=self.parse_detail, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('article.Teaser h2 a'):
            detail_url = data.css('::attr(href)').get()
            yield response.follow(url=detail_url, callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('h2.Core-title::text').get('').strip()
        item['Business_Type'] = response.css('span.Core-serviceText::text').get('').strip()
        item['Description'] = response.css('div.Core-description p::text').get('').strip()
        item['Phone Number'] = response.css('div[itemprop="telephone"]::text').get('').strip()
        item['Street Address'] = response.css('span.c-address-street-1::text').get('').strip()
        item['State'] = response.css('abbr[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://locations.moes.com/?_ga=2.224011803.1605964465.1665741463-51603040.1665741463'
        item['Lead_Source'] = 'locations.moes'
        item['Occupation'] = "Moe's Store"
        item['Record_Type'] = 'Business'
        yield item


