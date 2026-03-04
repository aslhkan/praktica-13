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
connection.commit()
connection.close()


