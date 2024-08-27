import scrapy


class DelawareScrapperSpider(scrapy.Spider):
    name = 'delaware_scrapper'
    start_urls = ['https://revenue.delaware.gov/business-license-search/']
    page_url = 'https://revenue.delaware.gov/business-license-search/page/{}/'

    custom_settings = {
        'FEED_URI': 'delaware_data.csv',
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
        for data in response.css('div.topicBlock'):
            item = dict()
            item['Business Name'] = data.css('h3::text').get().strip()
            item['License Number'] = data.css('.detail p:nth-child(1)::text').get('').strip().replace(
                'License Number : ', '')
            item['Business Activity'] = data.css('.detail p:nth-child(2)::text').get('').strip().replace('Business '
                                                                                                         'Activity : ',
                                                                                                         '')
            item['Valid From'] = data.css('.detail p:nth-child(3)::text').get('').strip().replace('Valid From : ', '')
            item['Valid To'] = data.css('.detail p:nth-child(4)::text').get('').strip().replace('Valid To : ', '')
            address = data.css('.detail p:nth-child(5)::text').get('').strip().replace('Location : ', '')
            if len(address.split(',')) > 1:
                new_add = address.split(',')[2].strip()
                if len(new_add.split(' ')) > 1:
                    item['State_Abrv'] = new_add.split(' ')[0]
                    item['Zip'] = new_add.split(' ')[1]
            item['Source_URL'] = 'https://revenue.delaware.gov/business-license-search/'
            item['Occupation'] = 'Revenue'
            item['Lead_Source'] = 'revenue.delaware'
            yield item

        total_pro = response.css('h2 span::text').get('').strip()
        total_pages = int(int(total_pro)/12) + 1
        for index in range(2, total_pages):
            yield scrapy.Request(url=self.page_url.format(index), callback=self.parse)
