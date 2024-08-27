import scrapy


class CliniclegalSpiderSpider(scrapy.Spider):
    name = 'cliniclegal_spider'
    start_urls = ['https://cliniclegal.org/find-legal-help/affiliates/directory']
    custom_settings = {
        'FEED_URI': 'cliniclegal.csv',
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
        for data in response.xpath('//table//tr/following-sibling::tr'):
            item = dict()
            item['Business Name'] = data.xpath('./td[@headers="view-display-name-table-column"]/text()').get('').strip()
            item['Phone Number'] = data.xpath('./td[@headers="view-phone-table-column"]/text()').get('').strip()
            item['Street Address'] = data.xpath('./td[@headers="view-street-address-table-column"]/text()').get('').strip()
            item['State'] = data.xpath('./td[@headers="view-state-province-id-table-column"]/text()').get('').strip()
            item['Zip'] = data.xpath('./td[@headers="view-postal-code-table-column"]/text()').get('').strip()
            item['Occupation'] = 'Legal Help'
            item['Source_URL'] = 'https://cliniclegal.org/find-legal-help/affiliates/directory'
            item['Lead_Source'] = 'cliniclegal'
            yield item
