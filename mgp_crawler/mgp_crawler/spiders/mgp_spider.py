import scrapy


class MgpSpiderSpider(scrapy.Spider):
    name = "mgp_spider"
    # Define the starting URL
    def start_requests(self):
        unprocess_pages = get_unprocessed_mgp_page_ids()
        assert unprocess_pages, "No unprocessed tfc pages."
        print(f"Unprocess Page: {unprocess_pages}")
        for page in unprocess_pages:
            url = f'https://tfc-taiwan.org.tw/articles/{page}'
            yield scrapy.Request(url=url, callback=self.parse, meta={'page': page})

    def parse(self, response):
        page_id = response.meta.get('page')
        # Check if the page exists by looking for a specific element
        if response.status == 200:
            # Extract desired content (for example, title or article text)
            title = response.xpath('//h1/text()').get()
            article = response.xpath('//div[contains(@class, "content-inner")]//text()').getall()

            # Clean up and join the article paragraphs
            article_content = ''.join(article).strip()
            # remove escaped characters
            article_content = re.sub(r'\s+', ' ', article_content).strip()
            article_content = article_content.replace('(function(d, s, id) { var js, fjs = d.getElementsByTagName(s)[0]; if (d.getElementById(id)) {return;} js = d.createElement(s); js.id = id; js.src = "//connect.facebook.net/zh_TW/all.js#xfbml=1"; fjs.parentNode.insertBefore(js, fjs); }(document, "script", "facebook-jssdk"));', '')
            article_content = article_content.replace('<!--/*--><![CDATA[/* ><!--*/ .container { width: 80%; margin: 0 auto; .section { margin: 20px 0; padding: 20px; border: 1px solid #ccc; border-radius: 8px; background-color: #e6e7e8; } .donate-link, .bank-account { display: flex; justify-content: center; align-items: center; background-color: #e6e7e8; /* 添加背景顏色 */ text-align: center; } .qrcode { width: 150px; height: 150px; } /*--><!]]>*/ 事實查核需要你的一份力量 捐款贊助我們 本中心查核作業獨立進行，不受捐助者影響。 台灣事實查核中心捐款連結 (或掃QR Code) /接受捐助準則','')

            # Yield a dictionary with extracted data
            yield {
                'source': 'tfc-taiwan',
                'page_id': page_id,
                'title': title,
                'content': article_content
            }
            # update db_info
            update_latest_tfc_page_id(page_id)
