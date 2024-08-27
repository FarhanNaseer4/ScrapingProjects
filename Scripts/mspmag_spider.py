import scrapy


class MspmagSpiderSpider(scrapy.Spider):
    name = 'mspmag_spider'
    start_urls = ['https://mspmag.com/search/location/doctors/#letter_filter=all&ord=alpha&page=1']
    custom_settings = {
        'FEED_URI': 'mspmag.csv',
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
        for data in response.css('div.loc_info h4 a'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, headers=self.headers)

        next_page = response.css('div.paginator_static a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        item['Business Name'] = response.css('div.mp_tag_cat_187 span::text').get('').strip()
        fullname = response.css('h1[itemprop="name"]::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['Last Name'] = fullname.split(',')[0].strip()
            item['First Name'] = fullname.split(',')[-1].strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Doctor'
        item['Business_Site'] = response.css('a[itemprop="url"]::attr(href)').get('').strip()
        item['Street Address'] = response.css('span[itemprop="streetAddress"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['State'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Category'] = response.css('div.mp_tag_cat_15 span::text').get('').strip()
        item['Phone Number'] = response.css('a[itemprop="tel"]::text').get('').strip()
        item['Lead_Source'] = 'mspmag'
        item['Record_Type'] = 'Person'
        item['Source_URL'] = 'https://mspmag.com/search/location/doctors/#letter_filter=all&ord=alpha&page=1'
        yield item
