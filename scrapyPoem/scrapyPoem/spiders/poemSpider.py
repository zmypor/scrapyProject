import scrapy
from scrapy import Request
from ..items import ScrapyPoemItem


class PoemspiderSpider(scrapy.Spider):
    name = 'poemSpider'  # 用于区别不同的爬虫
    allowed_domains = ['gushiwen.cn']  # 允许访问的域
    start_urls = ['http://so.gushiwen.cn/mingjus/']  # 爬取的地址

    def parse(self, response):
        # 先获每句名句的div
        for box in response.xpath('//*[@id="html"]/body/div[2]/div[1]/div[2]/div'):
            # 获取每句名句的链接
            url = 'https://so.gushiwen.cn' + box.xpath('.//@href').get()
            # 获取每句名句内容
            sentence = box.xpath('.//a[1]/text()').get()
            # 获取每句名句出处
            source = box.xpath('.//a[2]/text()').get()
            # 实例化容器
            item = ScrapyPoemItem()
            # 将收集到的信息封装起来
            item['url'] = url
            item['sentence'] = sentence
            item['source'] = source
            # 处理子页
            yield scrapy.Request(url=url, meta={'item': item}, callback=self.parse_detail)
        # 翻页
        next = response.xpath('//a[@class="amore"]/@href').get()
        if next is not None:
            next_url = 'https://so.gushiwen.cn' + next
            # 处理下一页内容
            yield Request(next_url)

    def parse_detail(self, response):
        # 获取名句的详细信息
        item = response.meta['item']
        content_list = response.xpath('//div[@class="contson"]//text()').getall()
        content = "".join(content_list).strip().replace('\n', '').replace('\u3000', '')
        item['content'] = content
        yield item