import scrapy


class CitySpiderSpider(scrapy.Spider):
    name = 'city_spider'
    start_urls = ['https://www.city-data.com/id-restaurants/']
    base_url = 'https://www.city-data.com/id-restaurants/{}'
    custom_settings = {
        'FEED_URI': 'city_data.csv',
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
        'authority': 'www.city-data.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '__utma=26892847.39389834.1663652252.1663652252.1663652252.1; __utmc=26892847; __utmz=26892847.1663652252.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; qcSxc=1663652252513; __qca=P0-330750274-1663652252507; __gads=ID=b2cf88cffe5b8c49-22053c70e4d500a7:T=1663652253:RT=1663652253:S=ALNI_Mb7-oqbyIA3LDdIuFEmfI2Mpbk7kw; __gpi=UID=00000add448f04ac:T=1663652253:RT=1663652253:S=ALNI_MZaOOTNdhPUqIQy4H2lX9cZjzGVjA; __utmb=26892847.9.9.1663652414009',
        'referer': 'https://www.city-data.com/city/Meadow-Utah.html',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
    }

    def parse(self, response):
        for data in response.css('div.table-responsive br + a'):
            url = data.css('::attr(href)').get()
            if not url.startswith(self.base_url):
                url = self.base_url.format(url)
            yield scrapy.Request(url=url, callback=self.parse_data, headers=self.headers)

    def parse_data(self, response):
        for data in response.xpath('//table[@id="restTAB"]//tr/following::tr'):
            item = dict()
            item['Business Name'] = data.css('td:nth-child(1) a::text').get('').strip()
            detail = data.css('td:nth-child(1) a::attr(href)').get('').strip()
            if detail:
                item['Detail_Url'] = self.base_url.format(detail)
            item['Street Address'] = data.css('td:nth-child(3)::text').get('').strip()
            item['Zip'] = data.css('td:nth-child(5)::text').get('').strip()
            item['State'] = data.css('td:nth-child(4)::text').get('').strip()
            item['Phone Number'] = data.css('td:nth-child(6)::text').get('').strip()
            item['Source_URL'] = 'https://city-data.com/city/Meadow-Utah.html'
            item['Lead_Source'] = 'city-data'
            item['Occupation'] = 'Restaurant'
            yield item


