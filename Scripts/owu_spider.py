import scrapy


class OwuSpiderSpider(scrapy.Spider):
    name = 'owu_spider'
    request_url = 'https://www.owu.edu/academics/faculty-staff-directory/letter/{}/'
    first_name = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
                  'U', 'V', 'W', 'X', 'Y', 'Z']
    custom_settings = {
        'FEED_URI': 'owu.csv',
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
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    }

    def start_requests(self):
        for first in self.first_name:
            yield scrapy.Request(url=self.request_url.format(first), callback=self.parse, headers=self.headers)

    def parse(self, response):
        for data in response.css('.directory_entry'):
            item = dict()
            item['Full Name'] = data.css('.directory_entry_name::text').get('').strip()
            item['Description'] = data.css('p.directory_entry_title::text').get('').strip()
            item['Phone Number'] = data.css('p.directory_entry_phone::text').get('').strip()
            item['Email'] = data.css('.table_cell_contact a::text').get('').strip()
            item['Occupation'] = 'Faculty & Staff'
            item['Source_URL'] = 'https://owu.edu/about/offices-services-directory/community-service-learning/our' \
                                 '-community-partners/ '
            item['Lead_Source'] = 'owu.edu'
            yield item
