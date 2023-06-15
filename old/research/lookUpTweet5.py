import mysql.connector as mydb

# コネクションの作成
conn = mydb.connect(
    host='localhost',
    port='3306',
    user='root',
    password='root',
    database='python_db'
)

print(conn.is_connected())