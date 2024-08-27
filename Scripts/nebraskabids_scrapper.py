import scrapy


class NebraskabidsScrapperSpider(scrapy.Spider):
    name = 'nebraskabids_scrapper'
    start_urls = ['https://www.nebraskabids.us/nebraska-contractors']
    base_url = 'https://www.nebraskabids.us{}'
    custom_settings = {
        'FEED_URI': 'nebraskabids_data.csv',
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
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
                  'application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    }

    def parse(self, response):
        for data in response.css('div.innertube .list-one'):
            url = data.css('.lr-mar a::attr(href)').get()
            if not url.startswith(self.base_url):
                url = self.base_url.format(url)
            yield scrapy.Request(url=url, callback=self.detail_page, headers=self.headers)

        next_page = response.xpath('//span[@class="page-link"]/a[contains(text(), "Next")]/@href').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse, headers=self.headers)

    def detail_page(self, response):
        item = dict()
        item['Business Name'] = response.xpath('//div[contains(@class,"info-gen-box")]//dt[contains(text(), '
                                               '"Company")]/following-sibling::dd/text()').get('').strip()
        item['Street Address'] = response.xpath('//div[contains(@class,"info-gen-box")]//dt[contains(text(), '
                                                '"Address")]/following-sibling::dd/text()').get('').strip()
        item['State'] = response.xpath('//div[contains(@class,"info-gen-box")]//dt[contains(text(), '
                                       '"State")]/following-sibling::dd/text()').get('').strip()
        item['Zip'] = response.xpath('//div[contains(@class,"info-gen-box")]//dt[contains(text(), '
                                     '"Zip")]/following-sibling::dd/text()').get('').strip()
        item['Phone Number'] = response.xpath('//div[contains(@class,"info-gen-box")]//dt[contains(text(), '
                                              '"Phone")]/following-sibling::dd/text()').get('').strip()
        item['Full Name'] = response.xpath('//div[contains(@class,"info-gen-box")]//dt[contains(text(), '
                                           '"Contact")]/following-sibling::dd/text()').get('').strip()
        item['Detail_Url'] = response.url
        item['Source_URL'] = 'https://www.nebraskabids.us/'
        item['Occupation'] = 'Service'
        item['Lead_Source'] = 'nebraskabids'
        item['Business_Type'] = 'Company'
        yield item
