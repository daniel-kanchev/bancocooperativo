import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from bancocooperativo.items import Article


class BancocooperativoSpider(scrapy.Spider):
    name = 'bancocooperativo'
    start_urls = ['https://blog.ruralvia.com/']

    def parse(self, response):
        links = response.xpath('//div[@class="btImageTextWidgetWraper"]/ul/li[1]//a/@href').getall()
        yield from response.follow_all(links, self.parse_next)

    def parse_next(self, response):
        yield response.follow(response.url, self.parse_article, dont_filter=True)

        next_article = response.xpath('//a[@class="btPrevNext btPrev"]/@href').get()
        if next_article:
            yield response.follow(next_article, self.parse_next)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1//span[@class="bt_bb_headline_content"]//text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="btArticleDate"]//text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="btContent"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
