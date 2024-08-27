import scrapy


class IvybusinessSpiderSpider(scrapy.Spider):
    name = 'ivybusiness_spider'
    start_urls = ['https://www.ivybusiness.iastate.edu/directory/']
    base_url = 'https://www.ivybusiness.iastate.edu/directory/{}'
    custom_settings = {
        'FEED_URI': 'ivybusiness.csv',
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
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/106.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    }

    def parse(self, response):
        for data in response.css('div.directory'):
            item = dict()
            fullname = data.css('a h3::text').get('').strip()
            if fullname:
                item['Full Name'] = fullname
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = fullname.split(' ')[-1].strip()
            item['Occupation'] = data.xpath('.//strong[contains(text(),"Title")]/following-sibling::text()').get('').strip()
            item['Category'] = data.xpath('.//strong[contains(text(),"Department")]/following-sibling::text()').get('').strip()
            item['Business Name'] = data.xpath('.//strong[contains(text(),"Office")]/following-sibling::text()').get('').strip()
            item['Phone Number'] = data.xpath('.//strong[contains(text(),"Phone")]/following-sibling::text()').get('').strip()
            item['Email'] = data.xpath('.//strong[contains(text(),"Email")]/following-sibling::a/text()').get('').strip()
            detail_url = data.css('div.col-md-5 a::attr(href)').get('').strip()
            if detail_url:
                item['Detail_Url'] = self.base_url.format(detail_url)
            item['Source_URL'] = 'https://www.ivybusiness.iastate.edu/directory/'
            item['Lead_Source'] = 'ivybusiness'
            item['Record_Type'] = 'Person'
            yield item

