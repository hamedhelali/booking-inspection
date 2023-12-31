import scrapy
from scrapy.http.request import Request
import re


class ReviewSpider(scrapy.Spider):
    def __init__(self, prop_url: str, *args, **kwargs):
        self.prop_url = prop_url
        super().__init__(*args, **kwargs)

    name = "review_spider"
    HEADERS = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36 Edg/87.0.664.66",
        'referer': None
    }

    def start_requests(self):
        async_id = self.prop_url.split("lrd=")[1].split(",")[0]
        ajax_url = "https://www.google.com/async/reviewDialog?async=feature_id:" + str(
            async_id) + ",start_index:0,_fmt:pc,sort_by:newestFirst"
        yield Request(url=ajax_url, headers=self.HEADERS, callback=self.get_total_iteration)
        #

    def get_total_iteration(self, response):
        total_reviews_text = response.css('.z5jxId::text').extract_first()
        total_reviews = int(re.sub(r'[^0-9]', '', total_reviews_text))

        print(total_reviews_text)
        print(total_reviews)

        temp = total_reviews / 10  # since
        new_num = int(temp)
        if temp > new_num:
            new_num += 1
        iteration_number = new_num

        j = 0
        print(iteration_number)
        if total_reviews > 10:
            for _ in range(0, iteration_number + 1):
                yield Request(url=response.request.url.replace('start_index:0', f'start_index:{j}'),
                              callback=self.parse_reviews, headers=self.HEADERS, dont_filter=True)
                j += 10
        else:
            yield Request(url=response.request.url, headers=self.HEADERS, callback=self.parse_reviews, dont_filter=True)

    def parse_reviews(self, response):
        print(response.url)
        all_reviews = response.xpath('//*[@id="reviewSort"]/div/div[2]/div')

        for review in all_reviews:
            # reviewer = review.css('div.TSUbDb a::text').extract_first()
            description_pieces = review.xpath('.//span[@class="review-full-text"]/text()').getall()
            description = ' '.join(description_pieces)
            # if description is None:
            #     description = review.css('.Jtu6Td span::text').extract_first()
            #     if description is None:
            #         description = ''

            if review.xpath('.//span[@class="lTi8oc z3HNkc"]/@aria-label').extract_first() is not None:
                review_rating = float(
                    review.xpath('.//span[@class="lTi8oc z3HNkc"]/@aria-label').extract_first().split(" ")[1])
            else:
                review_rating = None
            review_date = review.xpath('.//span[@class="dehysf lTi8oc"]/text()').extract_first()
            # yield {
            #     # "reviewer": reviewer,
            #     "description": description,
            #     "rating": review_rating,
            #     "review_date": review_date
            # }
    # def start_requests(self):
    #     start_url = f"https://www.goodreads.com/search?utf8=%E2%9C%93&query={self.book_title.replace(' ', '+')}"
    #     yield scrapy.Request(url=start_url, callback=self.parse)
    #
    # def parse(self, response):
    #     book_rel_url = response.css('td a::attr(href)').get()
    #     book_abs_url = response.urljoin(book_rel_url)
    #     yield scrapy.Request(book_abs_url, callback=self.review_parse)
    #
    # def review_parse(self, response):
    #     bt_text = response.css('h1::attr(aria-label)').get()
    #     book_title = bt_text.split(':')[1][1:]
    #     author = response.css('a span::text').getall()[1]
    #
    #     review_elements = response.css('section.ReviewText__content span')
    #     reviews_list = []
    #     for review in review_elements:
    #         review_text = ''.join(review.xpath('.//text()').getall())
    #         reviews_list.append(review_text)
    #
    #     yield {
    #         'book_tile': book_title,
    #         'author': author,
    #         'reviews': reviews_list
    #     }