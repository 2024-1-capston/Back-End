import pymysql

db = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='dochi', charset='utf8')

cursor = db.cursor()

sql = "select * from user"

cursor.execute(sql)

cursor.fetchall() #모든 행 가져오기

db.commit()
 
db.close()