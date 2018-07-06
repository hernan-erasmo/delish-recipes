# -*- coding: utf-8 -*-
import scrapy
import items
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class RecipiderSpider(CrawlSpider):
    name = 'recipider'
    allowed_domains = ['delish.com']
    start_urls = ['https://www.delish.com/cooking/recipe-ideas/']
    download_delay = 12.0

    rules = (
        Rule(LinkExtractor( restrict_css=('.full-item-image',)),
                            callback='parse_item',
                            follow=True),
    )

    def parse_item(self, response):
        item = items.Recipe()
        name = response.css('title::text')
        ingredients_list = response.css('div[class="ingredient-item"]')
        steps_list = response.css('div[class="direction-lists"]').css('li::text')
        
        try:
            item['name'] = self.sanitize_name(name.extract_first())
        except IndexError:
            self.logger.error('Error raised while parsing item title. Original will be left intact.')
            item['name'] = name.extract_first()

        item['ingredients'] = []
        item['steps'] = steps_list.extract()
        
        for i in ingredients_list:
            ingredient_amount = i.css('span[class="ingredient-amount"]::text')
            ingredient_description = i.css('span[class="ingredient-description"]::text')

            amount = ingredient_amount.extract_first()
            description = ingredient_description.extract_first()

            item['ingredients'].append({'amount': amount, 'description': description})

        yield item

    def sanitize_name(self, name):
        n = name.lower().split('how to make')[1].strip()
        return n.title()
