import  sqlite3
connection=sqlite3.connect("my_db.db")

cursor=connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users(
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
email TEXT NOT NULL,
age INTEGER
)
       '''        )
#cursor.execute('CREATE INDEX idx_email ON Users( email)')
cursor.execute('INSERT INTO Users(username,email,age) VALUES(?,?,?)',('newuser','newuser@exanpli.com','20'))
cursor.execute('INSERT INTO Users(username,email,age) VALUES(?,?,?)',('ODIN','ODIN@exanpli.com','300'))
# Выбираем всех пользователей
#cursor.execute('SELECT * FROM Users')
users = cursor.fetchall()
#cursor.execute('SELECT username, age FROM Users WHERE age > ?', (25,))
#results = cursor.fetchall()
# Получаем средний возраст пользователей для возраста
cursor.execute('SELECT age, AVG(age) FROM Users GROUP BY age')
results = cursor.fetchall()
cursor.execute('SELECT age, AVG(age) FROM Users GROUP BY age HAVING AVG(age) > ?', (30,))
cursor.execute('SELECT COUNT(*) FROM Users')
total_users = cursor.fetchone()[0]
cursor.execute('SELECT SUM(age) FROM Users')
total_age = cursor.fetchone()[0]

print('Общая сумма возрастов пользователей: ', total_age)

print('Общее количество пользователей:', total_users)
# Выбираем и сортируем пользователей по возрасту по убыванию
cursor.execute('SELECT AVG(age) FROM Users')
average_age = cursor.fetchone()[0]

print('Средний возраст пользователей: ', average_age)
cursor.execute('SELECT username, age FROM Users ORDER BY age DESC')
results = cursor.fetchall()
# Выбираем и сортируем пользователей по возрасту по убыванию
cursor.execute('SELECT username, age FROM Users ORDER BY age DESC')
results = cursor.fetchall()
# Выбираем и сортируем пользователей

cursor.execute(''' 
SELECT username, age, AVG(age) 
FROM Users 
GROUP BY age 
HAVING AVG(age) > ? 
ORDER BY age DESC 
''', (30,))
results = cursor.fetchall()

for row in results:
    print(row)
for row in results:
    print(row)
#for row in results:
    #print(row)
#for row in filtered_results:
   # print(row)
#for row in results:
  #  print(row)
#for row in results:
  #  print(row)
# Выводим результаты#for user in users:
    print(users)
#cursor.execute('UPDATE Users SET  age=? WHERE username=? ' ,(29,'newuser'))
#cursor.execute('DELETE  FROM Users   WHERE username=?',('newuser',))

connection.commit()
connection.close()


