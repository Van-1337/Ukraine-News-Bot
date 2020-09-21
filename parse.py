#!/usr/bin/env python
# -*- coding: utf-8 -*-
import const
import requests
import datetime
import json
import pyowm
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from time import sleep
import logging
owm = pyowm.OWM(const.OWMtoken, language="ru")
logging.basicConfig(filename="Parse.log", level=logging.INFO)
logging.info("START WORKING!")
log = logging.getLogger("ex")


# Дальше просто парсинг сайтов и выделение нужных вещей с помощью html, чтобы обработать их с помощью parse_mode='HTML'
def Course():
    logging.info("Get info about course")
    try:
        r = requests.get('https://kurs.com.ua/gorod/2249-harkov', headers={'User-Agent': UserAgent().chrome, 'Accept-Language': 'ru-RU, ru'})
        html = BeautifulSoup(r.content, 'html.parser')
        output = ""
        numb = 0
        for el in html.select('.course'):
            if numb % 4 == 2 or numb % 4 == 3:
                numb += 1
                continue
            elif numb % 4 == 0:
                whatis = "Продажа: "
                if numb == 0:
                    output += "<b>USD:</b>\n"
                elif numb == 4:
                    output += "<b>EUR:</b>\n"
                else:
                    output += "<b>RUB:</b>\n"
            else:
                whatis = "Покупка: "
            course = el.get_text().split()
            if (len(course) > 1):
                output += whatis + course[0] + ", " + course[1] + "\n"
            else:
                output += whatis + course[0] + "\n"
            if numb > 8:
                break
            numb += 1
        return output
    except Exception as e:
        log.exception("Error01")
        print (e)
        return "Произошла ошибка, курсы валют недоступны"

def Weather():
    logging.info("Get info about weather")
    try:
        fc = owm.three_hours_forecast("Kharkiv, UA")
        time = datetime.datetime.now() + datetime.timedelta(hours=const.deltahours)
        time = datetime.datetime(time.year, time.month, time.day, time.hour-(time.hour%3), 0) + datetime.timedelta(hours=3) #Приводим к ближайшему краному 3-м
        if time.hour>17:
            time = datetime.datetime(time.year, time.month, time.day, 9, 0) + datetime.timedelta(days=1)
        elif time.hour<9:
            time = datetime.datetime(time.year, time.month, time.day, 9, 0)
        output = "<b>Прогноз погоды</b> в Харькове на " + str(time.day) + "." + str(time.month) + ":\n"
        while time.hour<20:
            w=fc.get_weather_at(time)
            temp = w.get_temperature('celsius')["temp"]
            speed = w.get_wind()["speed"]
            humidity=w.get_humidity()
            output+= "<b>" + str(time.hour) + ":" + str(time.minute) + "0:</b> " + w.get_detailed_status() + ", температура: " + str(temp) + "°C, влажность: " + str(humidity) + "%, скорость ветра: " + str(speed) + " м/с\n"
            time=time + datetime.timedelta(hours=3)
        return output
    except Exception as e:
        log.exception("Error02")
        print (e)
        return "Произошла ошибка, погода недоступна"

def NewsWithAPI():
    logging.info("Get info about news with api")
    try:
        output="<b>Очередные новости:</b>\n"
        response = requests.get('http://newsapi.org/v2/top-headlines?country=ua&apiKey=' + const.NewsApiToken)
        data = json.loads(response.content)
        info=data["articles"]
        news=0
        for i in info:
            if (i["title"] and i["url"]):
                #output += "[" + i["title"] + "](" + i["url"] + ")"
                output += "•<a href=\"" + i["url"] + "\">" + i["title"] + "</a>"
            elif (i["title"]):
                output+=i["title"]
            if (i["description"]):
                output+="\n" + str(i["description"])
            output+="\n"
            news+=1
            if news>9:
                break
            #if (len(output)>700):
            #    break
        return output
    except Exception as e:
        log.exception("Error03")
        print (e)
        return "Произошла ошибка, новости от api недоступны"

def check_proxie(proxy): # {"http": 'http://xx.xx.xx.xx:xxxx'}
    if requests.get('https://8.8.8.8', proxies=proxy).status_code == 200:
        return 1
    else:
        return 0

def get_proxies():  # Парсит http прокси с сайта чтобы использовать их для подключения к яндексу их Украины
	maxproxies=10  # 10 штук хватит
	html=requests.get("http://foxtools.ru/Proxy?al=True&am=True&ah=True&ahs=True&http=True&https=False", headers={'User-Agent': UserAgent().chrome, 'Accept-Language': 'ru-RU, ru'})
	if html.status_code!=200:
		return []
	soup = BeautifulSoup(html.text, 'lxml') # pip install lxml
	line = soup.find('table', id='theProxyList').find('tbody').find_all('tr')
	correctproxies=[]

	for tr in line:
		td = tr.find_all('td')
		ip = td[1].text
		port = td[2].text
		country = td[3].text.replace('\xa0', '')
		time = td[6].text
		proxy={"http": 'http://' + ip + ":" + port}
		if (float(time)<1 and country!='Украина(UA)' and check_proxie(proxy)):
			correctproxies.append(proxy)
			if (len(correctproxies)>=maxproxies):
				break
	return correctproxies

def NewsYandex():  # отключено из-за неккоректной работы прокси
	correctproxies=get_proxies()
	if (len(correctproxies)>0):
		proxynow=0
		print ("Прокси доступно: ", correctproxies)
	else:
		return "Прокси-серверы недоступны("
	try:
		while (proxynow<len(correctproxies)):
			try:
				YaReq = requests.get('https://yandex.ua', headers={'User-Agent': UserAgent().chrome, 'Accept-Language': 'ru-RU, ru'}, proxies=correctproxies[proxynow])
				if YaReq.status_code==200:
					break
			except:
				proxynow+=1
				print ("Прокси не подошёл!")
		if YaReq.status_code!=200:
			return "Прокси не дали ответа"
		html = BeautifulSoup(YaReq.content, 'html.parser')
		output = "<b>Новости Яндекса:</b>\n"
		for el in html.findAll(attrs={"class":'home-link list__item-content list__item-content_with-icon home-link_black_yes'}):
			sleep(2)
			link = el.get('href')
			new = el.get('aria-label')
			Req2=YaReq
			while (proxynow<len(correctproxies)):
				try:
					Req2 = requests.get(link,headers={'User-Agent': UserAgent().chrome, 'Accept-Language': 'ru-RU, ru'}, proxies=correctproxies[proxynow])
					if Req2.status_code==200:
						break
				except:
					proxynow+=1
			if Req2.status_code!=200:
				return "Произошла ошибка, прокси были израсходованы("
			else:
				html2 = BeautifulSoup(Req2.content, 'html.parser')
				info = html2.findAll(attrs={"class": 'link link_theme_grey link_agency i-bem'})
				if (len(info) > 0):
					FinalLink = info[0].get('href')
				else:
					FinalLink = link
            #output+= "•[" + new + "](" +  FinalLink + ")\n"
				output += "•<a href=\"" + FinalLink + "\">" + new + "</a>\n"

        #for el in html.select('.news__item-content'):
        #    print (el)
		return output
	except Exception as e:

		print (e)
		return "Произошла ошибка, новости от яндекса недоступны"

def Corona():
    logging.info("Get info about corona")
    try:
        WorldReq = requests.get('https://www.worldometers.info/coronavirus/', headers={'User-Agent': UserAgent().chrome, 'Accept-Language': 'ru-RU, ru'})
        if WorldReq.status_code!=200:
            return "Сайт с коронавирусом недоступен"
        html = BeautifulSoup(WorldReq.content, 'html.parser')
        output = "<b>Коронавирус:</b>\n"
        numbers=[]
        for el in html.findAll(attrs={"class": 'maincounter-number'}):
            numbers.append(el.get_text().split())
        if len(numbers)>2:
            output+= "<b>Случаев заражения в мире</b>: " + numbers[0][0] + ", смертей: " + numbers[1][0] + ", вылечено: " + numbers[2][0] + "\n"

        UkraineReq = requests.get('https://www.worldometers.info/coronavirus/country/ukraine/', headers={'User-Agent': UserAgent().chrome, 'Accept-Language': 'ru-RU, ru'})
        html = BeautifulSoup(UkraineReq.content, 'html.parser')
        numbers = []
        for el in html.findAll(attrs={"class": 'maincounter-number'}):
            numbers.append(el.get_text().split())
        if len(numbers) > 2:
            output += "Случаев заражения <b>в Украине</b>: " + numbers[0][0] + ", смертей: " + numbers[1][0] + ", вылечено: "  + numbers[2][0] + "\n"
        info = html.findAll(attrs={"class": 'news_li'})[1].get_text().split()
        if (len(info)>2):
            output += "<b>В Украине вчера: </b>" + info[0] + " заражённых"
            if (len(info)>8):
                output += " и " + info[4] + " смертей"
        return output
    except Exception as e:
        log.exception("Error05")
        print (e)
        return "Произошла ошибка, новости про коронавирус недоступны"

def Holiday():
    logging.info("Get info about holiday")
    try:
        HolidayReq = requests.get('http://kakoysegodnyaprazdnik.ru/', headers={'User-Agent': UserAgent().chrome, 'Accept-Language': 'ru-RU, ru'})
        if HolidayReq.status_code != 200:
            return "Сайт с праздниками недоступен!"
        html = BeautifulSoup(HolidayReq.content, 'html.parser')
        output = "<b>Праздики сегодня:</b>\n"
        holidays = html.findAll('span', itemprop='text')
        if len(holidays)>2:
            output+=holidays[0].get_text() + "\n" + holidays[1].get_text() + "\n" + holidays[2].get_text()
        else:
            output+="Ошибка 05, праздников сегодня не будет("
        return output
    except Exception as e:
        log.exception("Error06")
        print (e)
        return "Произошла ошибка, информация про праздники недоступна"

def Shares():
    logging.info("Get info about shares")
    try:
        output="<b>Акции:</b>"
        links = [("Золото", "https://quote.rbc.ru/ticker/101039"), ("Серебро", "https://quote.rbc.ru/ticker/101041"), ("Нефть BRENT", "https://quote.rbc.ru/ticker/181206"), ("Газпром", "https://quote.rbc.ru/ticker/59768"), ("Google", "https://quote.rbc.ru/ticker/177723"), ("Apple", "https://quote.rbc.ru/ticker/177174"), ("Facebook", "https://quote.rbc.ru/ticker/177590"), ("Netflix", "https://quote.rbc.ru/ticker/177754"), ("Tesla", "https://quote.rbc.ru/ticker/177779"), ("Disney", "https://quote.rbc.ru/ticker/177472"), ("Coca-Cola", "https://quote.rbc.ru/ticker/177736")]
        for link in links:
            sleep(0.4)
            SharReq = requests.get(link[1], headers={'User-Agent': UserAgent().chrome, 'Accept-Language': 'ru-RU, ru'})
            if SharReq.status_code!=200:
                output+="\nакции " + links[0] + " недоступны"
            else:
                html = BeautifulSoup(SharReq.content, 'html.parser')
                akcii = html.findAll(attrs={"class": 'chart__info__sum'})
                if (len(akcii)>0):
                    output+="\n" + link[0] + ": " + akcii[0].get_text()
                akcii = html.findAll(attrs={"class": 'chart__info__change chart__change'})
                if (len(akcii)>0):
                    output+=" " + akcii[0].get_text().split()[0]
        return output
    except Exception as e:
        log.exception("Error07")
        print (e)
        return "Произошла ошибка, информация о акциях недоступна"

def KharkivNews():
    logging.info("Get info about kharkiv news")
    try:
        AmountNews=7
        output="<b>Харьковские новости:</b>\n"
        NewsReq = requests.get('https://mykharkov.info/news', headers={'User-Agent': UserAgent().chrome, 'Accept-Language': 'ru-RU, ru'})
        html = BeautifulSoup(NewsReq.content, 'html.parser')
        news=html.findAll(attrs={"class": 'name'})
        if (len(news)>=AmountNews):
            for i in range(AmountNews):
                output += "•<a href=\"" + news[i].get('href') + "\">" + news[i].get_text() + "</a>\n"
                #output+="[" + news[i].get_text() + "](" + news[i].get('href') + ")\n"
        else:
            output+="Сайт с новостями недоступен("
        return output
    except Exception as e:
        log.exception("Error08")
        print (e)
        return "Произошла ошибка, городские новости недоступны"


class GoogleNews:  #  Получение новостей с помощью Google News API
    @staticmethod
    def GetParse(text):
        data = json.loads(text)
        articleCount = data["articleCount"]
        info = data["articles"]
        del data
        result = ""
        for NumberNews in range(articleCount):
            article = info[NumberNews]
            result += "•<a href=\"" + article["url"] + "\">" + article["title"] + "</a> - " + article["source"]["name"]\
                      + "\n"
        return result

    @staticmethod
    def RequestWithFirstAPI(link):
        try:
            return requests.get(link+'?lang=ru&country=ua&image=optional&token='+const.GNews1Token)
        except:
            return 0

    @staticmethod
    def RequestWithSecondAPI(link):
        try:
            return requests.get(link+'?lang=ru&country=ua&image=optional&token='+const.GNews2Token)
        except:
            return 0

    @staticmethod
    def GetTopNews():
        response = GoogleNews.RequestWithFirstAPI('https://gnews.io/api/v3/top-news')
        if response != 0 and response.status_code == 200:
            return "<b>Главные новости:</b>\n" + GoogleNews.GetParse(response.content)
        return "Произошла ошибка, не удалось получить новости"

    @staticmethod
    def GetWorldNews():
        response = GoogleNews.RequestWithFirstAPI('https://gnews.io/api/v3/topics/world')
        if response != 0 and response.status_code == 200:
            return "<b>Мировые новости:</b>\n" + GoogleNews.GetParse(response.content)
        return "Произошла ошибка, не удалось получить новости"

    @staticmethod
    def GetUkrainianNews():
        response = GoogleNews.RequestWithFirstAPI('https://gnews.io/api/v3/topics/nation')
        if response != 0 and response.status_code == 200:
            return "<b>Украинские новости:</b>\n" + GoogleNews.GetParse(response.content)
        return "Произошла ошибка, не удалось получить новости"

    @staticmethod
    def GetTechnologyNews():
        response = GoogleNews.RequestWithSecondAPI('https://gnews.io/api/v3/topics/technology')
        if response != 0 and response.status_code == 200:
            return "<b>Новости технологий:</b>\n" + GoogleNews.GetParse(response.content)
        return "Произошла ошибка, не удалось получить новости"

    @staticmethod
    def GetSportsNews():
        response = GoogleNews.RequestWithSecondAPI('https://gnews.io/api/v3/topics/sports')
        if response != 0 and response.status_code == 200:
            return "<b>Спортивные новости:</b>\n" + GoogleNews.GetParse(response.content)
        return "Произошла ошибка, не удалось получить новости"

    @staticmethod
    def GetScienceNews():
        response = GoogleNews.RequestWithSecondAPI('https://gnews.io/api/v3/topics/science')
        if response != 0 and response.status_code == 200:
            return "<b>Новости науки:</b>\n" + GoogleNews.GetParse(response.content)
        return "Произошла ошибка, не удалось получить новости"


course="Информация недоступна"
weather="Информация недоступна"
newswithapi="Информация недоступна"
newsyandex="Информация недоступна"
corona="Информация недоступна"
holiday="Информация недоступна"
shares="Информация недоступна"
kharkivnews="Информация недоступна"
Gtopnews="Информация недоступна"
Gworldnews="Информация недоступна"
Gukrainiannews="Информация недоступна"
Gtechnologynews="Информация недоступна"
Gsportsnews="Информация недоступна"
Gsciencenews="Информация недоступна"


def Update():
    logging.info("Update all info")
    try:
        global course
        global weather
        global newswithapi
        global newsyandex
        global corona
        global holiday
        global shares
        global kharkivnews
        global Gtopnews
        global Gworldnews
        global Gukrainiannews
        global Gtechnologynews
        global Gsportsnews
        global Gsciencenews
    except:
        log.exception("No global variable")
        print ("Недостаёт глобальных переменных с хранением последних новостей!")
        return
    course = Course()
    weather = Weather()
    newswithapi = NewsWithAPI()
    #newsyandex = NewsYandex()
    corona = Corona()
    holiday = Holiday()
    shares = Shares()
    kharkivnews = KharkivNews()
    Gtopnews = GoogleNews.GetTopNews()
    Gworldnews = GoogleNews.GetWorldNews()
    Gukrainiannews = GoogleNews.GetUkrainianNews()
    Gtechnologynews = GoogleNews.GetTechnologyNews()
    Gsportsnews = GoogleNews.GetSportsNews()
    Gsciencenews = GoogleNews.GetScienceNews()
