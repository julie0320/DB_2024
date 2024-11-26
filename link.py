import psycopg2

connection = psycopg2.connect(
    user='project_17',
    password='3dibeu',
    host='140.117.68.66',
    port='5432',
    dbname='project_17'  # PostgreSQL 的資料庫名稱
)
cursor = connection.cursor()

