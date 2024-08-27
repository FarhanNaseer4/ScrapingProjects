import scrapy


class HickoryhillsilSpiderSpider(scrapy.Spider):
    name = 'hickoryhillsil_spider'
    start_urls = ['https://hickoryhillsil.org/business-directory/']
    custom_settings = {
        'FEED_URI': 'hickoryhillsil.csv',
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

    def parse(self, response):
        for data in response.xpath('//table//tr/following::tr'):
            item = dict()
            item['Business Name'] = data.xpath('./td[@class="column-1"]/text()').get('').strip()
            item['Street Address'] = data.xpath('./td[@class="column-3"]/text()').get('').strip()
            item['State_Abrv'] = data.xpath('./td[@class="column-4"]/text()').get('').strip()
            item['Phone Number'] = data.xpath('./td[@class="column-5"]/text()').get('').strip()
            item['Business_Site'] = data.xpath('./td[@class="column-6"]/a/text()').get('').strip()
            item['Occupation'] = data.xpath('./td[@class="column-7"]//text()').get('').strip()
            item['Description'] = data.xpath('./td[@class="column-2"]/text()').get('').strip()
            item['Source_URL'] = 'https://hickoryhillsil.org/business-directory/'
            item['Lead_Source'] = 'hickoryhillsil'
            yield item
