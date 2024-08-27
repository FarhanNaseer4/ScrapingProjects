import scrapy


class MethodistSpiderSpider(scrapy.Spider):
    name = 'methodist_spider'
    start_urls = ['https://www.methodist.edu/directory/']
    custom_settings = {
        'FEED_URI': 'methodist.csv',
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
        for data in response.css('a.people_item_name_link'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, headers=self.headers)

        next_page = response.css('a.next::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)

    def parse_detail(self, response):
        item = dict()
        fullname = response.css('h1.page_title::text').get('').strip()
        if fullname:
            item['Full Name'] = fullname
            item['First Name'] = fullname.split(' ')[0].strip()
            item['Last Name'] = fullname.split(' ')[-1].strip()
        item['Phone Number'] = response.css('div.phone a::text').get('').strip()
        item['Category'] = response.css('div.department a::text').get('').strip()
        item['Street Address'] = response.css('div.location div.contact_detail_info::text').get('').strip()
        item['Email'] = response.css('div.email a::text').get('').strip()
        item['Source_URL'] = 'https://www.methodist.edu/directory/'
        item['Occupation'] = response.css('p.page_description::text').get('').strip()
        item['Lead_Source'] = 'methodist'
        item['Record_Type'] = 'Person'
        item['Detail_Url'] = response.url
        yield item
