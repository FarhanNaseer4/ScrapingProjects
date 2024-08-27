import scrapy


class BusinessyabSpiderSpider(scrapy.Spider):
    name = 'businessyab_spider'
    start_urls = ['https://www.businessyab.com/directories.php']
    custom_settings = {
        'FEED_URI': 'businessyab.csv',
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
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    }

    def parse(self, response):
        for data in response.css('div.cat-box a:nth-child(2)'):
            cate_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=cate_url, callback=self.parse_listing, headers=self.headers)

    def parse_listing(self, response):
        for data in response.css('div.places-list'):
            item = dict()
            item['Business Name'] = data.css('h3 a::text').get('').strip()
            item['Detail_Url'] = data.css('h3 a::attr(href)').get('').strip()
            item['Occupation'] = data.css('a.place-cat::text').get('').strip()
            item['Category'] = ', '.join(cate.css('::text').get() for cate in data.css('a.place-cat'))
            address = data.css('p.place-address::text').get('').replace('Address:', '').strip()
            if len(address.split(',')) > 1:
                item['Street Address'] = address.split(',')[0].strip()
                state = address.split(',')[-2].strip()
                if len(state.split(' ')) > 1:
                    item['State_Abrv'] = state.split(' ')[0].strip()
                    item['Zip'] = state.split(' ')[-1].strip()

            item['Phone Number'] = data.css('div.explore-addr strong::text').get('').strip()
            item['Source_URL'] = 'https://www.businessyab.com/directories.php'
            item['Lead_Source'] = 'businessyab'
            yield item

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse_listing, headers=self.headers)
