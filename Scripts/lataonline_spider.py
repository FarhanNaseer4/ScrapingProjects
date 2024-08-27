import scrapy


class LataonlineSpiderSpider(scrapy.Spider):
    name = 'lataonline_spider'
    start_urls = ['https://lataonline.org/for-taxpayers/occupational-licenses/']
    custom_settings = {
        'FEED_URI': 'lataonline.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8',
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
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36 '
    }

    def parse(self, response):
        for data in response.xpath('//table//tr/following::tr'):
            item = dict()
            if data.css('td:nth-child(1) strong'):
                item['Business Name'] = data.css('td:nth-child(1) strong::text').get('').strip()

            else:
                name = data.css('td:nth-child(1)::text').get()
                if name:
                    item['Business Name'] = data.css('td:nth-child(1)::text').get('').strip()
            item['Category'] = data.css('td:nth-child(2)::text').get('').replace('*', '').strip()
            address = data.css('td:nth-child(3)::text').get('').strip()
            if address:
                item['Street Address'] = address.split(',')[0].strip()
                state = address.split(',')[-1].strip()
                if len(state.split(' ')) > 1:
                    item['State_Abrv'] = state.split(' ')[0].strip()
                    item['Zip'] = state.split(' ')[-1].strip()
            item['Phone Number'] = data.css('td:nth-child(4)::text').get('').strip()
            item['Occupation'] = 'Occupational Licenses'
            item['Source_URL'] = 'https://lataonline.org/for-taxpayers/occupational-licenses/'
            item['Lead_Source'] = 'lataonline'
            yield item


