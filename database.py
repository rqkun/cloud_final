## Connect to database and create table if it's not exist
import pyodbc

# Connect to database
con_str = ("Driver=ODBC Driver 17 for SQL Server; Server=sql8003.site4now.net; Database=db_aa2631_shoppingdb; UID=db_aa2631_shoppingdb_admin; PWD=12345asd; Trusted_Connection=no")
conn = pyodbc.connect(con_str)

cursor = conn.cursor()

# Create tables
cursor.execute('''IF OBJECT_ID(N'categories', N'U') IS NULL
				CREATE TABLE categories(
					categoryId int PRIMARY KEY,
					name nvarchar(MAX)
				)''')
conn.commit()

cursor.execute('''IF OBJECT_ID(N'users', N'U') IS NULL
				CREATE TABLE users(
					userId int PRIMARY KEY, 
					password nvarchar(MAX),
					email nvarchar(MAX),
					firstName nvarchar(MAX),
					lastName nvarchar(MAX),
					address1 nvarchar(MAX),
					address2 nvarchar(MAX),
					zipcode nvarchar(MAX),
					city nvarchar(MAX),
					state nvarchar(MAX),
					country nvarchar(MAX), 
					phone nvarchar(MAX)
				)''')
conn.commit()

cursor.execute('''IF OBJECT_ID(N'products', N'U') IS NULL
				CREATE TABLE products(
					productId int PRIMARY KEY,
					name nvarchar(MAX),
					price REAL,
					description nvarchar(MAX),
					image nvarchar(MAX),
					stock int,
					categoryId int,
					FOREIGN KEY(categoryId) REFERENCES categories(categoryId)
				)''')
conn.commit()

cursor.execute('''IF OBJECT_ID(N'kart', N'U') IS NULL
				CREATE TABLE kart(
					userId int,
					productId int,
					FOREIGN KEY(userId) REFERENCES users(userId),
					FOREIGN KEY(productId) REFERENCES products(productId)
				)''')
conn.commit()

#conn.close()

