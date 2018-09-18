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

#Массив в словарь
d = {'Ahour' : z[0], 'Amin' : z[1], 'Aweek' : z[2], 'Atsns' : z[3],  'Atemp1' : z[4],
        'Achns' : z[7], 'Arain' : z[8],  'Atemp2' : z[9]}

print 'Temp2:  ' + str(d['Atemp2'])
# Создаем соединение с файлом базы данных
conn = sqlite3.connect("/srv/www/aqstatus.db")

# Курсор - это специальный объект который делает запросы и получает их результаты
cursor = conn.cursor()

# Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
cursor.execute("""SELECT aqhour, aqchnsts
                FROM chnstat WHERE idch=(SELECT max(idch) FROM chnstat)""")
for row in cursor:
        print row

if d['Ahour'] != row[0]  or d['Achns'] != row[1] :

    now = round(time.time()) # округленное utime

    # SQL скрипт с подставновкой по порядку на места знаков вопросов:
    aqscript = """INSERT INTO chnstat(aqhour, aqmin, aqchnsts,  untme)
                 VALUES (?,?,?,?)"""

    # Аргументы для записи в таблицу
    newstrng = (d['Ahour'], d['Amin'], d['Achns'], now)

    try:
        cursor.execute(aqscript, newstrng)
        result = cursor.fetchall()
    except sqlite3.DatabaseError as err:
        print("Error: ", err)
    else:
        conn.commit() # Сохраняем изменения
        #print z[0]
        #print row[0]
        #print "------"


# Делаем SELECT запрос к базе данных, используя обычный SQL-синтаксис
cursor.execute("""SELECT aqhour, aqtemp1, aqtemp2, aqrnsens
                  FROM tempstat WHERE idt=(SELECT max(idt) FROM tempstat)""")
for row in cursor:
        print row

if d['Ahour'] != row[0]  or d['Atemp1'] != row[1] or d['Atemp2'] != row[2] or d['Arain'] != row[3]:

    now = round(time.time()) # округленное utime

    # SQL скрипт с подставновкой по порядку на места знаков вопросов:
    aqscript = """INSERT INTO tempstat(aqhour, aqmin, aqtemp1, aqtemp2, aqrnsens,
                  untme) VALUES (?,?,?,?,?,?)"""

    # Аргументы для записи в таблицу
    newstrng = (d['Ahour'], d['Amin'], d['Atemp1'], d['Atemp2'], d['Arain'], now)

    try:
        cursor.execute(aqscript, newstrng)
        result = cursor.fetchall()
    except sqlite3.DatabaseError as err:
        print("Error: ", err)
    else:
        conn.commit() # Сохраняем изменения
        #print z[0]
        #print row[0]
        #print "------"


# Закрываем соединение с базой данных
conn.close()
