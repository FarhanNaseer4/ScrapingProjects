import copy
import csv
import json
from datetime import datetime

import scrapy


class HiltonSpiderSpider(scrapy.Spider):
    name = 'hilton_spider'
    request_api = 'https://www.hilton.com/graphql/customer?operationName=geocode_hotelSummaryOptions&originalOpName=geocode_hotelSummaryOptions&appName=dx_shop_search_app&bl=en'
    custom_settings = {
        'FEED_URI': 'hilton.csv',
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
    payload = {
        "query": "query geocode_hotelSummaryOptions($address: String, $distanceUnit: HotelDistanceUnit, $language: "
                 "String!, $placeId: String, $queryLimit: Int!, $sessionToken: String) {\n  geocode(\n    language: "
                 "$language\n    address: $address\n    placeId: $placeId\n    sessionToken: $sessionToken\n  ) {\n   "
                 " match {\n      id\n      address {\n        city\n        country\n        state\n      }\n      "
                 "name\n      type\n      geometry {\n        location {\n          latitude\n          longitude\n   "
                 "     }\n        bounds {\n          northeast {\n            latitude\n            longitude\n      "
                 "    }\n          southwest {\n            latitude\n            longitude\n          }\n        }\n "
                 "     }\n    }\n    hotelSummaryOptions(distanceUnit: $distanceUnit, sortBy: distance) {\n      "
                 "bounds {\n        northeast {\n          latitude\n          longitude\n        }\n        "
                 "southwest {\n          latitude\n          longitude\n        }\n      }\n      amenities {\n       "
                 " id\n        name\n        hint\n      }\n      amenityCategories {\n        name\n        id\n     "
                 "   amenityIds\n      }\n      brands {\n        code\n        name\n      }\n      hotels(first: "
                 "$queryLimit) {\n        _id: ctyhocn\n        amenityIds\n        brandCode\n        ctyhocn\n      "
                 "  distance\n        distanceFmt\n        facilityOverview {\n          allowAdultsOnly\n        }\n "
                 "       name\n        display {\n          open\n          openDate\n          preOpenMsg\n          "
                 "resEnabled\n          resEnabledDate\n        }\n        contactInfo {\n          phoneNumber\n     "
                 "   }\n        address {\n          city\n          country\n          state\n        }\n        "
                 "localization {\n          coordinate {\n            latitude\n            longitude\n          }\n  "
                 "      }\n        masterImage(variant: searchPropertyImageThumbnail) {\n          altText\n          "
                 "variants {\n            size\n            url\n          }\n        }\n        "
                 "tripAdvisorLocationSummary {\n          numReviews\n          rating\n          ratingFmt(decimal: "
                 "1)\n          ratingImageUrl\n          reviews {\n            id\n            rating\n            "
                 "helpfulVotes\n            ratingImageUrl\n            text\n            travelDate\n            "
                 "user {\n              username\n            }\n            title\n          }\n        }\n        "
                 "leadRate {\n          hhonors {\n            lead {\n              dailyRmPointsRate\n              "
                 "dailyRmPointsRateNumFmt: dailyRmPointsRateFmt(hint: number)\n              ratePlan {\n             "
                 "   ratePlanName\n                ratePlanDesc\n              }\n            }\n            max {\n  "
                 "            rateAmount\n              rateAmountFmt\n              dailyRmPointsRate\n              "
                 "dailyRmPointsRateRoundFmt: dailyRmPointsRateFmt(hint: round)\n              "
                 "dailyRmPointsRateNumFmt: dailyRmPointsRateFmt(hint: number)\n              ratePlan {\n             "
                 "   ratePlanCode\n              }\n            }\n            min {\n              rateAmount("
                 "decimal: 1)\n              rateAmountFmt\n              dailyRmPointsRate\n              "
                 "dailyRmPointsRateRoundFmt: dailyRmPointsRateFmt(hint: round)\n              "
                 "dailyRmPointsRateNumFmt: dailyRmPointsRateFmt(hint: number)\n              ratePlan {\n             "
                 "   ratePlanCode\n              }\n            }\n          }\n        }\n      }\n    }\n  }\n}",
        "operationName": "geocode_hotelSummaryOptions",
        "variables": {
            "address": "AL",
            "language": "en",
            "placeId": None,
            "queryLimit": 150
        }
    }
    headers = {
        'authority': 'www.hilton.com',
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'authorization': 'Bearer DX.eyJhbGciOiJSU0EtT0FFUCIsImVuYyI6IkEyNTZHQ00iLCJwaWQiOiJ3ZWIiLCJraWQiOiI4UVl1RTZfdHBValdjUmVnem1RZFlBaF9RYlk1ckVqUlpPTThwWmNKeU5BIn0.tCnKab428cbzqCLXYHf0c-w0ETTGfylnpFeQ3jxmCXTUSdH8ZzpsGh0tPGzPzE44GTznTKZoFNJkcU0Ry1rj76oqwCsYqN8ngGPpFo5_PIwUMFRnupvOJ6GLKOnmlTRwgc0cjnbMQ0EYlP2_IBPHeqIYniV9fQKw13TbVZH5STUBGndX-VEWwzIl-R1iikX6zz2pxD0PlWUtbO4zA2zuwuGn9OHje1gH6_mMZIl0aawcSfyOnlc_Za3469ifhq92e0qjFUdGtkoWM2-J19psAboOQ8riLyoUddjGx7qVz5V6R9gswps6XCO5ns5qzp7Xu79FmEmWgKRkWi005aIZgw.nAEHBbfdw-4cn0bb._3VFDA-LRWZ62348P9TSZfH5WOCWwxSkSOWb8dlZwEkxjEujGw-mgy4GrwuPsjkPxnpCTYaIBjPTo_HqcBOTuZecSz3s9zv_Gg3bYfrfZ7ppkYkvaA_khDyTy99V5wA8CsuOTkDakhY4BMki93vR_e9RvbbC2OistBosuQMmTMsnK1aaBNrTfDIKlPgZjnClrxmla9OQmFyI4nXktraFQTmEfEcxv1qh8QWGxgfpRtXsY8dziUaskZEteroQLx9Hg9YvhFpgBCTLja3td6dEFcYlpOE_Eu1iJZi9iecApnRT69d6r0tA6hnxNmUm5xnE5_Bb2XoSV_tVJQfk0E0KDD4EBzP0OGY3jQ4CUWXMxg5Fh6gkPkFKAtj67ydDr0XDB7ZfbLv78HMhcroXIjOkdRR4EFqmf9V7pmg7ltJua6lZ8_N465kqsfwZMxg3MWOOxZX7h1zCYAnnx6q1L3lEKmq8kqClWAd-VQ3BcaOQEAHzDXN8Y28nIXyiZ_NxQ2ygcxEz9w0VZ9IyORujPL6u03R93Jhx_jXrxa1NHt2o12LoeMU5WfdwvuS5MuTK_pxVSelA-GbfGT6wUCny7kiHd9sOCCZtMS7j__10Nga5Fvui1oLNb2KG-2p2dPlIrBECRZsi9YiNXQv6U2A6insZ526XUPqhvgf9CEpjUFvw11kcEih7Pfs.wgdrWEDDV8fDsf7Wt3GJ0A',
        'content-type': 'application/json',
        'cookie': 'rxVisitor=166764548263126K76314S0PDC6T2TV1MDCN05ACUAVBP; visitorId=ace818b7-f353-4435-a69b-1671ca460df2; ftr_ncd=6; s_ecid=MCMID%7C83449446810377738063019141072489627433; aam_uuid=83428009214300187213021496479230512742; __qca=P0-74666474-1667645487416; __lt__cid=093cd327-2500-4349-9aa6-c19dbdc587b8; __lt__cid.47135154=093cd327-2500-4349-9aa6-c19dbdc587b8; _gcl_au=1.1.628162449.1667645489; _pin_unauth=dWlkPU16UTBabU0xT0RZdFpHUmlaUzAwT1RJM0xXSXdaR0V0TVdGaE5EZGlPR1ZoWkdGbQ; AKA_A2=A; akacd_ohw_prd_external=3845255182~rv=23~id=93b875e9bfb435a1d8d8a1d1575d937c; bm_sz=6F90BA78D8DA860D34BE33CA18AAD205~YAAQ1G0/FxFoHjKEAQAA2cXEUBHyvRneg5/HH94HaV6+/iUhi1+abqpjyQhhYvyDfUEg5rrENDM0rYSSg1ueWLeF3jeM/Zna0wnNJQI9597epTKzfDXBv0Z9pNdrdha3fUTZLOY5rudmMCp+oIIpX437Dg5TjD0Ss3Qbk83AKK9G/RWOHjt+vpVVTPAf36gqsRZPZlufsHIAxfexr4c6gEDCCEdCmnt1HwEjm8wJhOtk+X+mg+toxRRhcOp7lXIZHEbEM7VKhddBRa0qU9heX9wn3VYbhq3EVU1X7se9iA9Mnmo=~4538947~4605490; ak_bmsc=B3EB129CA20CAD3C79F18ED011C60D5D~000000000000000000000000000000~YAAQ1G0/FxJoHjKEAQAAFdXEUBFEilrfebk0gjjEs0QtCSNXEMml76Nkj2QIgmNJw1Bi55KeztYqOLaQNNrKYR9OhrchYSabb7061asmWDsT3Xk5m48J0vuEtXsKeQxBbDlrPQhSeg5ioqK5j3o75JmFLNQbKd3xK8zKlgUpgv3b2+gYIK0BI7LEpdbNInWqSt99WeyjbMOSuMY5hHwodPlmLGOipr/RiEt4Z+HUCgzJno0OXflB8CU4kU+2PY0PpAVJubUElQ7e/ogB5V+uh1+l0oAyCe1vGIQ51jb5S9g8bXmM0gDrgdPStbH/g7OQkt+28ke7bQpAyWkx0hYU4Vpam5ezML+s4zpJpnugtHqFCi2wIHnG4Cwiw7MxjUl3gCxQ+5zL25EoMJUV6cFbowzs+6uLz0kaTpnFyaYc4FC1nBc=; _abck=3BFB72EABF8A24F44CFCD3E45A91CA79~0~YAAQ1G0/FxVoHjKEAQAAAdfEUAhaDIyk1avOgZL6wfuEVxhnA+NNS7FBOn1BbtU2Y6GzvefRwv9egER6ZYoycsNz5ek4/Nm+FS8iUEmIsuFH2Rq0+gVj7rOxcJoOqFaozhEIARZNa0fXnaHZsDBHqyOllZP+s4aCfGHYGlp+nmNnoIOVzPouLTwHmrVdr0ynVizgR6K+P+ddhBI0zT2/r+ofMiQqvBWs0doYKsShtAbQifYZiLgZi5/AD7pYtpjF5IG5es4Vh7YHq3CY3WC/8ODIbDSnHsmeOO904qxXYt8KJb13kEwLma0aIQFc05amT6aNao+6a/rOT3CFxol+srcWbAqtBXkcYJ0lsC68XwifXNwaIGLCOg6lh+UkR3FPeewkIdiXIiSeQMq/FNePifDASof58cGxvA/4YrvA4V9/f1p5DBfNflT8Hd4Cv4/7yItLphyexm/c~-1~-1~1667805884; dtCookie=v_4_srv_2_sn_PJ5GQF96JGCHV80J1K21J901MVHFL2AI_app-3A0da30f11c94bda74_1_ol_0_perc_100000_mul_1_rcs-3Acss_0; AMCVS_F0C120B3534685700A490D45%40AdobeOrg=1; AMCV_F0C120B3534685700A490D45%40AdobeOrg=1176715910%7CMCIDTS%7C19304%7CMCMID%7C83449446810377738063019141072489627433%7CMCAAMLH-1668407199%7C3%7CMCAAMB-1668407199%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1667809599s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C5.4.0; s_cc=true; _hp_ses.05ab=*; TMS=web%3D17836315%2CWeb-app%3D19485237%2Cweb-app%3D19484989%2Cweb%3D20222786%2Cweb-app%3D15300019%2Cweb-app%3D21881915%2Cweb-app%3D22525083%2Cweb-app%3D22989791%2Cweb-app%3D23364969%2Cweb-app%3D24568600%2Cweb%3D25075844%2Cweb%3D25075845%2Cweb%3D25075847; ftr_blst_1h=1667802401897; __lt__sid=e67fc6fc-1c05409f; __lt__sid.47135154=e67fc6fc-1c05409f; ln_or=d; gpv_v9=Browser%3AEN%3Ahilton-garden-inn%3ASearch%3ASearch%20Results; ADRUM=s=1667802494743&r=https%3A%2F%2Fwww.hilton.com%2Fen%2Fsearch%2Fhilton-garden-inn%2F%3Fhash%3D-1370461696; dtSa=-; notice_behavior=none; forterToken=a4bab3822d6b4d00a2240b7ac006b7e0_1667802503247__UDF43_9ck; _hp_id.05ab=937c3278-0798-4fbd-a490-28cf9061087a.1667645488.2.1667802508.1667645544.c7dc8560-3d58-4b15-b8ef-7ec33da7b267; RT="z=1&dm=hilton.com&si=510e53ae-4594-47ab-9ebb-6e69e92be646&ss=la6eh95f&sl=3&tt=144s&se=p0&bcn=%2F%2F684d0d48.akstat.io%2F&ld=2ria"; _uetsid=289bdeb05e6511eda1c0975b57988319; _uetvid=ce6597205cf711eda7996991562971ac; bm_sv=85FD50A46E47885F8EFC55563BD0DC3F~YAAQ1G0/F71pHjKEAQAA2UnIUBE/ZRFoVzz+KQCagFPcNeSoqoFDO/ih0iADyU/P6qmKzVOgvPpcsJLLoW8mW3dq7uHuRMg8S+fhXVvfLK+im3c0eM5mohNFpwy0zQdDnL9SyiCaxghvvSqnnXURl0NOaYqqHPcsYwCYCCwvHI5m9qdidZzqsVOxfXvqBcUkiS08KYZnZq839ap2DEscSwS0Bt7Orcjmz8TAnda56u6PMJm2IN1PzWSi4gTYj6Pa5cI=~1; dtLatC=123; s_sq=hiltonglobalprod%3D%2526c.%2526a.%2526activitymap.%2526page%253DBrowser%25253AEN%25253Ahilton-garden-inn%25253ASearch%25253ASearch%252520Results%2526link%253DUpdate%2526region%253D__next%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253DBrowser%25253AEN%25253Ahilton-garden-inn%25253ASearch%25253ASearch%252520Results%2526pidt%253D1%2526oid%253DUpdate%2526oidt%253D3%2526ot%253DSUBMIT; lastAdobeEvent=%22chatPresented%22; rxvt=1667804434230|1667802385993; dtPC=2$402495371_865h363vRWPRDOHJHREMJGLKNPRMJFRQLKOREMLJ-0e0; _abck=3BFB72EABF8A24F44CFCD3E45A91CA79~-1~YAAQDKwwF8zv3zWEAQAA+cHKUAg/JOY30UACRLFFeHypfjLWaJdxx3bkWRCOMrIr031cdibaLWBvaeu+YUM3mrmdsiswuf0r1qMNzB33wbie1QD74w6DuCEX1JcGbak3ddIZ+b16tNbcy5LrPqJU6cfmN45N7bG/jlAjBkC+M4as41UFAJE6PtCM7WH2Gy1Y40byOSB6LwAM8MUVTMsW3HrvyokvyANdM38ei/PNlL5fy4Agp/SYWuB2diYhpWhXQxqrjoNLGe+iPPgeXb5SdPiN2udub5IEIZAyLOEBIf+mifwyrQpyCZBpg2otgHIrGfK5UHP8YYiFtD83ZDpCv5Wy7ZG6eIbXtcRh83uHK8eDaNI38ogfI5gfgDUaO3dNZb1A10dibl8K6c8UfqvNDQQrgaffcTa6Bnx559F7E3JIYAOvl26kJkl1y5otnGQFG4EuhDAhPFhy~0~-1~1667805884; bm_sv=85FD50A46E47885F8EFC55563BD0DC3F~YAAQDKwwF83v3zWEAQAA+cHKUBExQ0gpaiJVo+nz5Kjg1frw/qXGb22TMh1hn19gonGFojaUQrAdX357jgRVIrvPwcDtX8V6tF36w9ogBPgncIsY4UrMoHxveLoaojt26+94xdn7qFmrpEWATxpqU8/MjLWtB+q5vtnQJvgBZtrXvfRLG4VFnDOmEmQ08anxXc3uX7Nd+oSE+x+a0cq5ZliuM3bDXguv57Oh9s+TeqabfmBNdS6/Ylp5udT2+p+y5XY=~1',
        'dx-platform': 'web',
        'origin': 'https://www.hilton.com',
        'referer': 'https://www.hilton.com/en/search/hilton-garden-inn/',
        'sec-ch-ua': '"Google Chrome";v="107", "Chromium";v="107", "Not=A?Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
        'x-dtpc': '2$402495371_865h363vRWPRDOHJHREMJGLKNPRMJFRQLKOREMLJ-0e0',
        'x-dtreferer': 'https://www.hilton.com/en/search/hilton-garden-inn/?query=Alabama%252C%2520US&placeId=&arrivalDate=2022-11-07&departureDate=2022-11-08&flexibleDates=false&numRooms=1&numAdults=1&numChildren=0&room1ChildAges=&room1AdultAges=&specialRateTokens=&awc=&cid=&dclid=&gclid=&wtmcid=&displayCurrency=LOCAL&adjoiningRoomStay=false&sessionToken=ace818b7-f353-4435-a69b-1671ca460df2'
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.request_state = self.get_search_state()

    def get_search_state(self):
        with open('states.csv', 'r', encoding='utf-8-sig') as reader:
            return list(csv.DictReader(reader))

    def start_requests(self):
        for state in self.request_state:
            payload = copy.deepcopy(self.payload)
            payload['variables']['address'] = state.get('States', '')
            yield scrapy.Request(url=self.request_api, method='POST', callback=self.parse,
                                 headers=self.headers, body=json.dumps(payload))

    def parse(self, response):
        json_result = json.loads(response.body)
        detail_data = json_result.get('data', {}).get('geocode', {}).get('hotelSummaryOptions', {}).get('hotels', [])
        for result in detail_data:
            item = dict()
            item['Business Name'] = result.get('name', '')
            item['Street Address'] = result.get('address', {}).get('city', '')
            item['State'] = result.get('address', {}).get('state', '')
            item['Phone Number'] = result.get('contactInfo', {}).get('phoneNumber', '')
            item['Latitude'] = result.get('localization', {}).get('coordinate', '').get('latitude', '')
            item['Longitude'] = result.get('localization', {}).get('coordinate', '').get('longitude', '')
            item['Source_URL'] = 'https://www.hilton.com/en/search/hilton-garden-inn'
            item['Meta_Description'] = 'Hilton Garden Inn offers worry-free reservations and affordable hotel rooms.'
            item['Occupation'] = 'Hotel'
            item['Lead_Source'] = 'hilton'
            item['Record_Type'] = 'Business'
            item['Scraped_date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            yield item
