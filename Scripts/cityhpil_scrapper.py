import scrapy


class CityhpilScrapperSpider(scrapy.Spider):
    name = 'cityhpil_scrapper'
    start_urls = ['https://cityhpil.com/business_directory/index.php']
    custom_settings = {
        'FEED_URI': 'cityhpil_data.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address', 'License '
                                                                                                          'Number',
                               'Business Activity', 'Valid From',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Phone_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation']

    }

    def parse(self, response):
        for data in response.css('table.table  :last-child tr'):
            item = dict()
            business_name = data.css('td a[target]::text').get('').strip()
            if business_name:
                item['Business Name'] = business_name
            else:
                item['Business Name'] = data.css('td:nth-child(1)::text').get('').strip()

            item['Street Address'] = data.css('td:nth-child(2)::text').get('').strip()
            item['Category'] = data.css('td:nth-child(3)::text').get('').strip()
            item['Phone Number'] = data.css('td:nth-child(4) a::text').get('').strip()
            item['Source_URL'] = 'https://cityhpil.com/business_directory/index.php'
            item['Occupation'] = 'Revenue'
            item['Lead_Source'] = 'cityhpil'
            item['Business_Site'] = data.css('td a[target]::attr(href)').get('').strip()
            yield item
