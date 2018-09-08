#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
# Импортируем библиотеку, соответствующую типу нашей базы данных
import telnetlib
import sqlite3
#from datetime import datetime
import time
import sys

try:
    tn = telnetlib.Telnet("192.168.31.36", 23, 3)
except:
    print 'Error telnet'
    sys.exit(0)
tn.write("zapr vsep")  # делаем запрос
tn.read_until("vse param+") # читаем начиная с конца этой строки
s = tn.read_until("\n") # заканчиваем чтение на элементе '\n'
tn.close()
z = s.split('+')  # разбиваем полученное в массив по элементу '+'
z.pop()  # удаляем последний элемент '\n'

# 0-часы, 1-минуты, 2-день недели, 3-ДТ включ, 4-температ1
# 5-часы след вкл, 6-мин след вкл, 7-каналы включены сейчас,
# 8- нет дождя (то +10) + следующий канал , 9-температура 2
print s  # печатаем принятое и обрезанное

# Преобразуем текстовый массив в int
for i, item in enumerate(z):
    z[i] = int(item)

# Вычисление состояния датчика дождя
if z[8] > 10:
    z[8] = 0
else:
    z[8] = 1

xx = len(z)  # количество элементов (для проверки)
print xx    # печать к-ва элементов
print z


# Создаем соединение с файлом базы данных
conn = sqlite3.connect("/srv/www/aqstatus.db")

# Курсор - это специальный объект который делает запросы и получает их результаты
cursor = conn.cursor()

# Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
cursor.execute("""SELECT aqhour, aqmin, aqchnsts,
             aqtemp1, aqtemp2, aqrnsens FROM aqstatus WHERE id=(SELECT max(id) FROM aqstatus)""")
for row in cursor:
        print row

if z[0] == row[0]  and z[7] == row[2] and  z[4] == row[3] and z[9] == row[4] and z[8] == row[5]:
    print 'Exit wo!'
    sys.exit(0)
else:
    now = round(time.time()) # округленное utime

    # SQL скрипт с подставновкой по порядку на места знаков вопросов:
    aqscript = """INSERT INTO aqstatus(aqhour, aqmin, aqwkday, aqchnsts,
                aqtemp1, aqtemp2, aqrnsens, untme) VALUES (?,?,?,?,?,?,?,?)"""

    # Аргументы для записи в таблицу
    newstrng = (z[0],z[1], z[2], z[7], z[4], z[9], z[8], now)

    try:
        cursor.execute(aqscript, newstrng)
        result = cursor.fetchall()
    except sqlite3.DatabaseError as err:
        print("Error: ", err)
    else:
        conn.commit() # Сохраняем изменения
        print z[0]
        print row[0]
        print "------"

# Закрываем соединение с базой данных
conn.close()