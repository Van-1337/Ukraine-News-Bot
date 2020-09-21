#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ВСЕ ТОКЕНЫ МОГУТ БЫТЬ ПОЛУЧЕНЫ ПО БЕСПЛАТНЫМ ТАРИФАМ
TelegramToken = '1111111111:aaaaabbbbbcccccdddddeeeeefffffggggg' # Получить в телеграмме у @BotFather
OWMtoken = '1234567890aabbccddeeff1234567890' # https://openweathermap.org/api
NewsApiToken = '1234567890aabbccddeeff1234567890' # newsapi.org
GNews1Token = '1234567890aabbccddeeff1234567890' # первый api полученный в https://gnews.io/
GNews2Token = '1234567890aabbccddeeff1234567890' # второй api полученный в https://gnews.io/

deltahours=0 # Отличие между временем в Украине и временем на сервере. То есть если на сервере 10 часов, а в Украине 11,
# то эта переменная должна быть равна 1. (может быть отрицательной)
timetoprepare=2 # количество минут для сбора информации на всех сайтах перед публикацией.
# Чем медленнее интернет на сервере, тем должна быть больше

sources="Курсы валют: https://kurs.com.ua/gorod/2249-harkov\n" \
        "Погода: https://openweathermap.org\n" \
        "Новости: gnews.io newsapi.org mykharkov.info\n" \
        "Коронавирус: https://www.worldometers.info/coronavirus\n" \
        "Праздники: http://kakoysegodnyaprazdnik.ru\n" \
        "Акции: https://quote.rbc.ru"
