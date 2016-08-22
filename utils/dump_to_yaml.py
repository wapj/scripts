#!/usr/bin/env python
import sys
import pymysql

if len(sys.argv) < 2:
    print("테이블 명을 입력해주세요.")
    print("usage : dumpto_yaml.py <table_name>")
    print("ex : dumpto_yaml.py mydb.users")
    print("ex : dumpto_yaml.py mydb.users id=123")
    exit(1)

connection = pymysql.connect(host='localhost', user='', password='', charset='utf8mb4', cursorclass=pymysql.cursors.DictCursor)
table_name = sys.argv[1]
field = []


def select_desc():
    with connection.cursor() as cursor:
        sql = "desc " + table_name
        cursor.execute(sql)
        result = cursor.fetchall()
        return result


def select_table():
    result = select_desc()
    select_query = "SELECT "
    for r in result:
        field.append(r['Field'])
        select_query += " `%s`," % (r['Field'])

    select_query = select_query[:len(select_query) -1] + " FROM " + table_name

    # 조건문이 있는경우는 넣어줌
    if len(sys.argv) > 2:
        select_query = select_query + " WHERE " + sys.argv[2]

    with connection.cursor() as cursor:
        cursor.execute(select_query)
        result = cursor.fetchall()
        return result


def dump_yaml():
    print('%s:' % table_name)
    for row in select_table():
        print('-')
        for f in field:
            print("    " + f + ": " + str(row[f]))


dump_yaml()
