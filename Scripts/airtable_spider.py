import json
from datetime import datetime

import scrapy


class AirtableSpiderSpider(scrapy.Spider):
    name = 'airtable_spider'
    request_api = 'https://airtable.com/v0.3/view/viwGKjLp92jKggHwg/readSharedViewData?stringifiedObjectParams=%7B' \
                  '%22shouldUseNestedResponseFormat%22%3Atrue%7D&requestId=reqt4lDTRqXXaYkhP&accessPolicy=%7B' \
                  '%22allowedActions%22%3A%5B%7B%22modelClassName%22%3A%22view%22%2C%22modelIdSelector%22%3A' \
                  '%22viwGKjLp92jKggHwg%22%2C%22action%22%3A%22readSharedViewData%22%7D%2C%7B%22modelClassName%22%3A' \
                  '%22view%22%2C%22modelIdSelector%22%3A%22viwGKjLp92jKggHwg%22%2C%22action%22%3A' \
                  '%22getMetadataForPrinting%22%7D%2C%7B%22modelClassName%22%3A%22view%22%2C%22modelIdSelector%22%3A' \
                  '%22viwGKjLp92jKggHwg%22%2C%22action%22%3A%22readSignedAttachmentUrls%22%7D%2C%7B%22modelClassName' \
                  '%22%3A%22row%22%2C%22modelIdSelector%22%3A%22rows%20*%5BdisplayedInView%3DviwGKjLp92jKggHwg%5D%22' \
                  '%2C%22action%22%3A%22createBoxDocumentSession%22%7D%2C%7B%22modelClassName%22%3A%22row%22%2C' \
                  '%22modelIdSelector%22%3A%22rows%20*%5BdisplayedInView%3DviwGKjLp92jKggHwg%5D%22%2C%22action%22%3A' \
                  '%22createDocumentPreviewSession%22%7D%2C%7B%22modelClassName%22%3A%22view%22%2C%22modelIdSelector' \
                  '%22%3A%22viwGKjLp92jKggHwg%22%2C%22action%22%3A%22downloadCsv%22%7D%2C%7B%22modelClassName%22%3A' \
                  '%22view%22%2C%22modelIdSelector%22%3A%22viwGKjLp92jKggHwg%22%2C%22action%22%3A%22downloadICal%22' \
                  '%7D%2C%7B%22modelClassName%22%3A%22row%22%2C%22modelIdSelector%22%3A%22rows%20*%5BdisplayedInView' \
                  '%3DviwGKjLp92jKggHwg%5D%22%2C%22action%22%3A%22downloadAttachment%22%7D%5D%2C%22shareId%22%3A' \
                  '%22shrRdOr8zNFFPKYVJ%22%2C%22applicationId%22%3A%22appaNdEJJDKEpqiR9%22%2C%22generationNumber%22' \
                  '%3A0%2C%22expires%22%3A%222022-11-24T00%3A00%3A00.000Z%22%2C%22signature%22%3A' \
                  '%223de808d47118aaa0621cb49f8c0d4791961d275ee3a3980a32e40fc9fab929db%22%7D '
    custom_settings = {
        'FEED_URI': 'airtable.csv',
        'FEED_FORMAT': 'csv',
        'FEED_EXPORT_ENCODING': 'utf-8-sig',
        'FEED_EXPORT_FIELDS': ['Business Name', 'Full Name', 'First Name', 'Last Name', 'Street Address',
                               'Valid To', 'State', 'Zip', 'Description', 'Phone Number', 'Phone Number 1', 'Email',
                               'Business_Site', 'Social_Media', 'Record_Type',
                               'Category', 'Rating', 'Reviews', 'Source_URL', 'Detail_Url', 'Services',
                               'Latitude', 'Longitude', 'Occupation',
                               'Business_Type', 'Lead_Source', 'State_Abrv', 'State_TZ', 'State_Type',
                               'SIC_Sectors', 'SIC_Categories',
                               'SIC_Industries', 'NAICS_Code', 'Quick_Occupation', 'Scraped_date', 'Meta_Description']
    }
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Connection': 'keep-alive',
        'Cookie': 'brw=brwZ3hya6rwqr31e4; __Host-airtable-session=eyJzZXNzaW9uSWQiOiJzZXNCbDByNHdVb3BOTWZ1WCIsImNzcmZTZWNyZXQiOiJMNnJaNGRUa3ZHdWxjVWg1aVBYVExrWVcifQ==; __Host-airtable-session.sig=dyiwCB-9jzg4HRrnBEFdnXZS_wm1pplo-PCXuap7s_M; lightstep_guid%2FsharedViewOrApp=4e4803d0794d8c43; lightstep_session_id=5f9bef2e200d1c0d; AWSELB=F5E9CFCB0C87D62DB5D03914FDC2A2D2D45FBECE9253BE434965F4D2126129E0338EBA226991AC3560650744EDFEAB3519A6F71FB96B33102AACBD69B157E29A353EDE523E; AWSELBCORS=F5E9CFCB0C87D62DB5D03914FDC2A2D2D45FBECE9253BE434965F4D2126129E0338EBA226991AC3560650744EDFEAB3519A6F71FB96B33102AACBD69B157E29A353EDE523E; brw=brwZ3hya6rwqr31e4',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'ot-tracer-sampled': 'true',
        'ot-tracer-spanid': '2b9b3cfe228b877c',
        'ot-tracer-traceid': '3008c31e5fca7c6e',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'x-airtable-application-id': 'appaNdEJJDKEpqiR9',
        'x-airtable-inter-service-client': 'webClient',
        'x-airtable-page-load-id': 'pglMUcfbzjAqo3V20',
        'x-early-prefetch': 'true',
        'x-time-zone': 'Asia/Karachi',
        'x-user-locale': 'en'
    }

    def start_requests(self):
        yield scrapy.Request(url=self.request_api, callback=self.parse, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.body)
        rows = result.get('data', {}).get('table', {}).get('rows', [])
        for row in rows:
            item = dict()
            item['Business Name'] = row.get('cellValuesByColumnId', {}).get('fldJBRoylGFvETSgD', '')
            fullname = row.get('cellValuesByColumnId', {}).get('fldaEEshTXGCKEFez', '')
            if fullname:
                item['Full Name'] = fullname
                item['First Name'] = fullname.split(' ')[0].strip()
                item['Last Name'] = fullname.split(' ')[-1].strip()
            item['Phone Number'] = row.get('cellValuesByColumnId', {}).get('fld1KUySAdKL6mn5J', '')
            address = row.get('cellValuesByColumnId', {}).get('fldPKqXCnAhHgn0ra', '')
            if len(address.split(',')) > 1:
                item['Street Address'] = address.split(',')[0].strip()
                state = address.split(',')[-1].strip()
                if len(state.split(' ')) > 1:
                    item['State'] = state.split(' ')[0].strip()
                    item['Zip'] = state.split(' ')[-1].strip()
            else:
                item['Street Address'] = address
            item['Email'] = row.get('cellValuesByColumnId', {}).get('fld1IuKEIDqElES2g', '')
            item['Meta_Description'] = 'Explore the All Businesses view on Airtable.'
            item['Source_URL'] = 'https://airtable.com/shrRdOr8zNFFPKYVJ/tblYhr1rDGT7FobKD'
            item['Lead_Source'] = 'airtable'
            item['Occupation'] = 'Business Service'
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item
