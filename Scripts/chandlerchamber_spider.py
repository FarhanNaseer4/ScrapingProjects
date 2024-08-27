import scrapy


class ChandlerchamberSpiderSpider(scrapy.Spider):
    name = 'chandlerchamber_spider'
    start_urls = ['https://business.chandlerchamber.com/list/search?sa=true']
    custom_settings = {
        'FEED_URI': 'business_chandlerchamber.csv',
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
        for data in response.css('div.gz-list-card-wrapper div.card-header a'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.detail_page, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.css('div.fl-rich-text h1::text').get('').strip()
        item['Street Address'] = response.css('span.gz-street-address::text').get('').strip()
        item['State_Abrv'] = response.css('span[itemprop="addressRegion"]::text').get('').strip()
        item['Zip'] = response.css('span[itemprop="postalCode"]::text').get('').strip()
        item['Occupation'] = response.css('span.gz-cat::text').get('').strip()
        item['Phone Number'] = response.css('span[itemprop="telephone"]::text').get('').strip()
        item['Business_Site'] = response.css('li.gz-card-website a::attr(href)').get('').strip()
        item['Social_Media'] = ', '.join(data.css('::attr(href)').get('') for data in response.css('li.gz-card-social a'))
        fullname = response.css('div.gz-member-repname::text').get()
        if fullname:
            item['Full Name'] = fullname
            if len(fullname.split(' ')) > 1:
                item['First Name'] = fullname.split(' ')[0]
                item['Last Name'] = fullname.split(' ')[-1]
        item['Source_URL'] = 'https://business.chandlerchamber.com/list'
        item['Lead_Source'] = 'business.chandlerchamber'
        item['Detail_Url'] = response.url
        yield item

