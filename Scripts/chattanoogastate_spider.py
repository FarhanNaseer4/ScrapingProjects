import scrapy


class ChattanoogastateSpiderSpider(scrapy.Spider):
    name = 'chattanoogastate_spider'
    start_urls = ['https://directory.chattanoogastate.edu/']
    custom_settings = {
        'FEED_URI': 'chattanoogastate.csv',
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
        for data in response.xpath('//table//tr/following::tr'):
            item = dict()
            item['First Name'] = data.css('td.views-field-field-first-name p::text').get('').strip()
            item['Last Name'] = data.css('td.views-field-field-last-name::text').get('').strip()
            item['Full Name'] = item['First Name'] + ' ' + item['Last Name']
            item['Occupation'] = data.css('td.views-field-field-job-title::text').get('').strip()
            item['Phone Number'] = data.css('td.views-field-field-phone a::text').get('').strip()
            item['Email'] = data.css('td.views-field-field-e-mail::text').get('').strip()
            item['Lead_Source'] = 'directory.chattanoogastate'
            item['Record_Type'] = 'Person'
            item['Source_URL'] = 'https://directory.chattanoogastate.edu/'
            yield item

        next_page = response.css('li.next a::attr(href)').get('').strip()
        if next_page:
            yield response.follow(url=next_page, callback=self.parse, headers=self.headers)
