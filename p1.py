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
# Выбираем всех пользователей
cursor.execute('SELECT * FROM Users')
users = cursor.fetchall()

# Преобразуем результаты в список словарей
users_list = []
for user in users:
    user_dict = {
    'id': user[0],
    'username': user[1],
    'email': user[2],
    'age': user[3]
    }
    users_list.append(user_dict)

# Выводим результаты
for user in users_list:
    print(user)
print('Общая сумма возрастов пользователей: ', total_age)

print('Общее количество пользователей:', total_users)
cursor.execute('SELECT MAX(age) FROM Users')
max_age = cursor.fetchone()[0]

print('Максимальный возраст среди пользователей:', max_age)

# Выбираем и сортируем пользователей по возрасту по убыванию
cursor.execute('SELECT AVG(age) FROM Users')
average_age = cursor.fetchone()[0]
cursor.execute('SELECT MIN(age) FROM Users')
min_age = cursor.fetchone()[0]

print('Минимальный возраст среди пользователей: ', min_age)
print('Средний возраст пользователей: ', average_age)
cursor.execute('SELECT username, age FROM Users ORDER BY age DESC')
results = cursor.fetchall()
# Выбираем и сортируем пользователей по возрасту по убыванию
cursor.execute('SELECT username, age FROM Users ORDER BY age DESC')
results = cursor.fetchall()
# Выбираем и сортируем пользователей

