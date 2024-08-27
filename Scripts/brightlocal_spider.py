import scrapy


class BrightlocalSpiderSpider(scrapy.Spider):
    name = 'brightlocal_spider'
    start_urls = ['https://www.brightlocal.com/agency-directory/#']
    custom_settings = {
        'FEED_URI': 'brightlocal.csv',
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
        for data in response.css('div.Home-statesContainer div.Home-statesCitiesListItem a'):
            comp_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=comp_url, callback=self.get_company_data, headers=self.headers)

    def get_company_data(self, response):
        for data in response.css('div.State-citiesColumnsContainer div a'):
            city_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=city_url, callback=self.get_listing, headers=self.headers)

    def get_listing(self, response):
        for data in response.css('div[data-id="Digital Marketing"] div.AgencyCard-container '
                                 'div.AgencyCard-ratingStarsAndNameContainer a'):
            detail_url = data.css('::attr(href)').get()
            yield scrapy.Request(url=detail_url, callback=self.get_details, headers=self.headers)

    def get_details(self, response):
        item = dict()
        item['Business Name'] = response.css('h1.CompanyProfile-agencyName::text').get('').strip()
        address = response.xpath('//div[@class="CompanyProfile-location"]/span/following-sibling::text()').get(
            '').strip()
        if address:
            item['Street Address'] = address.split(',')[0].strip()
            item['Zip'] = address.split(',')[-1].strip()
        item['Description'] = response.css('div.CompanyProfile-description::text').get('').strip()
        item['Category'] = response.xpath('//li[contains(@class, "Categories-categoryItem")]/span/following-sibling'
                                          '::text()').get('').strip()
        item['Phone Number'] = response.css('a.ContactDetails-phone::text').get('').strip()
        item['Detail_Url'] = response.url
        item['Occupation'] = 'Business Services'
        item['Source_URL'] = 'https://www.brightlocal.com/agency-directory/#'
        item['Lead_Source'] = 'brightlocal'
        yield item
