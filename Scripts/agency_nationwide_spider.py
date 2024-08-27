import scrapy


class AgencyNationwideSpiderSpider(scrapy.Spider):
    name = 'agency_nationwide_spider'
    start_urls = ['https://agency.nationwide.com/search']
    base_url = 'https://agency.nationwide.com/{}'
    detail_url = 'https://agency.nationwide.com{}'
    custom_settings = {
        'FEED_URI': 'agency_nationwides.csv',
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
        'authority': 'agency.nationwide.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.css('li.Directory-listItem a'):
            city_url = data.css('::attr(href)').get()
            if not city_url.startswith(self.base_url):
                city_url = self.base_url.format(city_url)
            yield scrapy.Request(url=city_url, callback=self.get_listing_url, headers=self.headers)

    def get_listing_url(self, response):
        for data in response.css('li.Directory-listItem a'):
            list_url = data.css('::attr(href)').get()
            if not list_url.startswith(self.base_url):
                list_url = self.base_url.format(list_url)
            yield scrapy.Request(url=list_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('li.Directory-listTeaser'):
            item = dict()
            item['Business Name'] = data.css('h3[itemprop="name"]::text').get('').strip()
            item['Phone Number'] = data.css('span[itemprop="telephone"]::text').get('').strip()
            item['Street Address'] = data.css('span.c-address-street-1::text').get('').strip()
            item['State_Abrv'] = data.css('abbr[itemprop="addressRegion"]::text').get('').strip()
            item['Zip'] = data.css('span[itemprop="postalCode"]::text').get('').strip()
            item['Email'] = data.css('a.Teaser-emailCta::attr(href)').get('').strip().replace('mailto:', '')
            detail_url = data.css('a.Teaser-titleLink::attr(href)').get('').replace('.', '')
            if detail_url:
                item['Detail_Url'] = self.detail_url.format(detail_url)
            item['Occupation'] = 'Agents'
            item['Source_URL'] = 'https://agency.nationwide.com/search'
            item['Lead_Source'] = 'agency.nationwide'
            yield item
