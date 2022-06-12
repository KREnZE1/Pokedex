import scrapy  # Library for the basis of web-scraping
import mysql.connector  # Library for connecting the program with the MySQL-database
import re  # Library for using REGEX


class PokedexSpider(scrapy.Spider):
    name = 'pokedex'  # Name of the spider
    start_urls = ['https://bulbapedia.bulbagarden.net/wiki/Bulbasaur_(Pok%C3%A9mon)']  # Link where the spider starts to search

    # noinspection PyMethodOverriding
    def parse(self, response):
        number = response.xpath('//big//big//a//span/text()').get()  # gets the Pokédex number on the current page
        name = response.xpath('//tr//td//big//big//b/text()').get()  # gets the name of the Pokémon on the current page
        type1 = response.xpath('//td//a//span//b/text()').get()  # gets the typing of the Pokémon on the current page
        type2 = None  # Some Pokémon only have one type, so more logic is required
        xpath = response.xpath('//tbody//tr//td//a//span//b/text()').getall()[1]  # gets the second entry, which corresponds to the second type or unknown
        if xpath != "Unknown":  # If the second type is not unknown (Unknown means the type doesn't exist, so a Pokémon with only one type)
            type2 = xpath  # the second type is set to the entry on the current page
        obj = "".join(response.xpath('//table//tbody//tr//td/text()').getall())  # Pathway to the height and weight is not definitive, so all possible entries are joined into one string
        height = re.search("\\d?\\d\\.?\\d\\d?\\sm", obj).group()  # Height is always written in the format "XX.XX m", so the REGEX searches for that
        weight = re.search("\\d{1,3}\\.?\\d{1,3}\\skg", obj).group()  # Weight is always written in the format "XXX.XX kg", so the REGEX searches for that

        # not executable, because the user and password aren't correct
        mydb = mysql.connector.connect(host="localhost", user="user", password="password", database="webscrape",
                                       port=3306)  # Connection to the database is established
        cursor = mydb.cursor()  # Object to execute SQL-Statements is created
        sql = "INSERT INTO pokemon_expanded VALUES (%s, %s, %s, %s, %s, %s)"  # SQL-Statement is formed
        val = (number, name, type1, type2, height, weight)  # Data of the Pokémon is put together
        cursor.execute(sql, val, False)  # SQL-Statement and arguments are combined and sent to the database
        mydb.commit()  # Statement is executed in the database

        url = response.xpath('//tr//td//a/@href')[5].get()  # Gets the link extension for the next Pokémon
        link = response.urljoin(url)  # and combines it with the basis of the link to form the link for the next Pokémon
        yield scrapy.Request(link, callback=self.parse)  # Method calls itself recursively to go to the next Pokémon
