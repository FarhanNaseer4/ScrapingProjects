import scrapy


class BroadbandsearchSpiderSpider(scrapy.Spider):
    name = 'broadbandsearch_spider'
    start_urls = ['https://www.broadbandsearch.net/provider']
    base_url = 'https://www.broadbandsearch.net{}'
    next_page = 'https://www.broadbandsearch.net/provider{}'
    custom_settings = {
        'FEED_URI': 'broadbandsearch.csv',
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
        for data in response.css('div.row-cols-md-4 article'):
            item = dict()
            item['Business Name'] = data.css('span[itemprop="name"]::text').get('').strip()
            item['Phone Number'] = data.css('span[itemprop="telephone"]::text').get('').strip()
            business = data.css('a.position-relative::attr(href)').get()
            if business:
                if not business.startswith(self.base_url):
                    business = self.base_url.format(business)
                item['Business_Site'] = business
            item['Description'] = data.css('span.card-body::text').get('').strip()
            item['Occupation'] = 'Internet Providers'
            item['Source_URL'] = 'https://broadbandsearch.net/service/michigan/omer'
            item['Lead_Source'] = 'broadbandsearch'
            yield item

        next_page = response.css('a[title="Next Page"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=self.next_page.format(next_page), callback=self.parse)

