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
try:
    # Начинаем транзакцию
    cursor.execute('BEGIN')

    # Выполняем операции
    cursor.execute('INSERT INTO Users (username, email) VALUES (? , ?)', ('user1', 'user1@example.com'))
    cursor.execute('INSERT INTO Users (username, email) VALUES (? , ?)', ('user2', 'user2@example.com'))

    # Подтверждаем изменения
    cursor.execute('COMMIT')

except:
    # Отменяем транзакцию в случае ошибки
    cursor.execute('ROLLBACK')

# Закрываем соединение
connection.close()
