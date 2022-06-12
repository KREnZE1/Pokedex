import scrapy
import mysql.connector
import re


class PokedexSpider(scrapy.Spider):
    name = 'pokedex'
    start_urls = ['https://bulbapedia.bulbagarden.net/wiki/Bulbasaur_(Pok%C3%A9mon)']

    # noinspection PyMethodOverriding
    def parse(self, response):
        number = response.xpath('//big//big//a//span/text()').get()
        name = response.xpath('//tr//td//big//big//b/text()').get()
        type1 = response.xpath('//td//a//span//b/text()').get()
        type2 = None
        xpath = response.xpath('//tbody//tr//td//a//span//b/text()').getall()[1]
        if xpath != "Unknown":
            type2 = xpath
        obj = "".join(response.xpath('//table//tbody//tr//td/text()').getall())
        height = re.search("\\d?\\d\\.?\\d\\d?\\sm", obj).group()
        weight = re.search("\\d{1,3}\\.?\\d{1,3}\\skg", obj).group()

        #not executable, because the user and password aren't correct
        mydb = mysql.connector.connect(host="localhost", user="user", password="password", database="webscrape",
                                       port=3306)
        cursor = mydb.cursor()
        sql = "INSERT INTO pokemon_expanded VALUES (%s, %s, %s, %s, %s, %s)"
        val = (number, name, type1, type2, height, weight)
        cursor.execute(sql, val, False)
        mydb.commit()

        url = response.xpath('//tr//td//a/@href')[5].get()
        link = response.urljoin(url)
        yield scrapy.Request(link, callback=self.parse)
