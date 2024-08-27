import scrapy


class BusinessfinderSpiderSpider(scrapy.Spider):
    name = 'businessfinder_spider'
    start_urls = ['https://businessfinder.mlive.com/MI-Omer']
    base_url = 'https://businessfinder.mlive.com{}'
    custom_settings = {
        'FEED_URI': 'businessfinder.csv',
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
        'Accept-Language': ' en-US,en;q=0.9',
        'Cache-Control': ' max-age=0',
        'Connection': ' keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/105.0.0.0 Safari/537.36',
    }

    def parse(self, response):
        for data in response.css('div.group li a'):
            url = data.css('::attr(href)').get()
            if not url.startswith(self.base_url):
                url = self.base_url.format(url)
            yield scrapy.Request(url=url, callback=self.parse_data, headers=self.headers)

    def parse_data(self,response):
        check_data = response.css('div#center_content h4::text').get('')
        if 'Sorry, there were no results' in check_data:
            pass
        else:
            for data in response.css('div.resultInner '):
                item = dict()
                item['Business Name'] = data.css('h3 a::text').get('').strip()
                item['Zip'] = data.css('p.address span.zip::text').get('').strip()
                item['Street Address'] = data.css('p.address::text').get('').strip().replace(',', '')
                item['Phone Number'] = data.css('p span.tel::text').get('').strip()
                item['Detail_Url'] = self.base_url.format(data.css('h3 a::attr(href)').get())
                item['Source_URL'] = 'https://businessfinder.mlive.com/MI-Omer'
                item['Lead_Source'] = 'businessfinder.mlive'
                item['Occupation'] = response.css('h2 strong::text').get('').strip()
                yield item

        next_page = response.xpath('//ul/li/a[contains(text(), "Next")]/@href').get()
        if next_page:
            yield scrapy.Request(url=self.base_url.format(next_page), callback=self.parse_data, headers=self.headers)