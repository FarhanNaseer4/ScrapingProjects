import scrapy


class DirectorySpiderSpider(scrapy.Spider):
    name = 'directory_spider'
    start_urls = ['https://directory.5280.com/?search_type=doctor&s&submit=Search']
    custom_settings = {
        'FEED_URI': 'directory_5280.csv',
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
        for data in response.css('header.listing-header'):
            item = dict()
            fullname = data.css('h1[itemprop="name"] a::text').get()
            if fullname:
                item['Full Name'] = fullname.strip()
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = fullname.split(' ')[-1].strip()
            item['Street Address'] = data.css('span[itemprop="streetAddress"]::text').get('').strip()
            item['State_Abrv'] = data.css('span[itemprop="addressRegion"]::text').get('').strip()
            item['Zip'] = data.css('span[itemprop="postalCode"]::text').get('').strip()
            item['Occupation'] = 'Doctors'
            item['Phone Number'] = data.css('span[itemprop="telephone"]::text').get('').strip()
            item['Business_Site'] = data.css('a[itemprop="url"]::attr(href)').get('').strip()
            item['Category'] = data.css('span.listing-categories a::text').get('').strip()
            item['Source_URL'] = 'https://directory.5280.com/?search_type=doctor&s&submit=Search'
            item['Lead_Source'] = 'directory.5280'
            item['Detail_Url'] = data.css('h1[itemprop="name"] a::attr(href)').get()
            yield item

        next_page = response.css('span.next a::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=next_page, callback=self.parse, headers=self.headers)
