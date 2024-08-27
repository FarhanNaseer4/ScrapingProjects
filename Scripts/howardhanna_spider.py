import scrapy


class HowardhannaSpiderSpider(scrapy.Spider):
    name = 'howardhanna_spider'
    start_urls = ['https://www.howardhanna.com/agent/search']
    base_url = 'https://www.howardhanna.com{}'
    custom_settings = {
        'FEED_URI': 'howardhanna.csv',
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
        'authority': 'www.howardhanna.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': '_ga=GA1.2.550826590.1663569776; _gid=GA1.2.1263280817.1663569776; _fbp=fb.1.1663569779475.718016252; _gcl_au=1.1.199591614.1663569783; rl_visitor_history=829a58ad-5c34-45a6-8021-5bf15367aae2; sifi_user_id=A6EE7A2C541B4CC9ACD809D3CA4A9CF6; _clck=1pdwbpk|1|f50|0; __hstc=49138489.568c4dd35a2336819de12297c4c28f55.1663569784238.1663569784238.1663569784238.1; hubspotutk=568c4dd35a2336819de12297c4c28f55; __hssrc=1; __RequestVerificationToken=AflnKWr-bA_c5K81EDmHoUwMSAUADnnC2cy1d8WXvJvrS8q5synpKBTj_nnMUsERhdT8_Tx0GCsfDcWo2lJxLRZFsWMRZt-EoyI7ZNUF9zLYz4YOejgDOeX8WVAI-OZeYbEx1Q2; _dc_gtm_UA-1425924-1=1; _clsk=403wux|1663570073720|6|1|n.clarity.ms/collect; _uetsid=4c1890f037e611ed9aac874169d8ff2d; _uetvid=4c18ea4037e611edb31c79c34c309e8b; __hssc=49138489.6.1663569784238; cto_bundle=Jvmgl185QWNyYmM2TFNHaDJUTjNnMWlhYWZ6MDc2dmtaa0p1SEd3REdQWnFGQk92JTJCR0JldDZwUk5TVGlESjFoRm02RnVIbjV4UmhnZEdnczZrUEo2aTVnNG4yY2ZhUFJncHklMkZVNGJ5SSUyRlZhOFNkOE00eVp3TGxyVjB2UlRYTUZ2a2klMkZRWE1DcFhheWE4T3VxbkFpUWQlMkZGSSUyQmclM0QlM0Q',
        'referer': 'https://www.howardhanna.com/',
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
        for data in response.css('div.alpha li a'):
            url = data.css('::attr(href)').get()
            if not url.startswith(self.base_url):
                url = self.base_url.format(url)
            yield scrapy.Request(url=url, callback=self.parse_data, headers=self.headers)

    def parse_data(self, response):
        for data in response.css('div.card-entity'):
            item = dict()
            fullname = data.css('a.titleUnderlined::text').get('').strip()
            item['Full Name'] = fullname
            if len(fullname.split(' ')) > 1:
                if len(fullname.split(' ')) > 2:
                    item['First Name'] = fullname.split(' ')[0].strip()
                    item['Last Name'] = fullname.split(' ')[2].strip()
                else:
                    item['First Name'] = fullname.split(' ')[0].strip()
                    item['Last Name'] = fullname.split(' ')[1].strip()
            item['Phone Number'] = data.css('table tr:nth-child(2) td.text-grey a::text').get('').strip()
            detail_url = data.css('a.titleUnderlined::attr(href)').get()
            if detail_url:
                if not detail_url.startswith(self.base_url):
                    detail_url = self.base_url.format(detail_url)
                item['Detail_Url'] = detail_url
                yield scrapy.Request(url=detail_url, callback=self.detail_page, meta={'item': item},
                                     headers=self.headers)

        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse_data, headers=self.headers)

    def detail_page(self, response):
        item = response.meta['item']
        item['Phone Number 1'] = response.css('a.agent-phone::text').get('').strip()
        item['Business Name'] = response.css('div.p-b-5 a::text').get('').strip()
        business = response.css('div.p-b-5 a::attr(href)').get('').strip()
        if business:
            item['Business_Site'] = self.base_url.format(response.css('div.p-b-5 a::attr(href)').get('').strip())
        item['Social Media'] = ', '.join(data.css('::attr(href)').get() for data in response.css('div.icons-social a'))
        item['Source_URL'] = 'https://howardhanna.com/'
        item['Lead_Source'] = 'howardhanna'
        item['Occupation'] = 'Realtor'
        yield item
