from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

user = User(name = 'nothing')
session.add(user)
session.commit

categories = ['Electronics', 'Cars', 'Clothes']
for i in categories:
	x = Category(name = i)
	session.add(x)
	session.commit()

items = ['iPhone 5', 'iPhone 5C', 'iPhone 6', 'iPad 2', 'iPad 3', 'iPad 4']
for i in items:
	x = Item(name = i, category_id = 1)
	session.add(x)
	session.commit()

items = ['Mustang', 'Civic', 'Jeep', 'Truck', 'Tesla']
for i in items:
	x = Item(name = i, category_id = 2)
	session.add(x)
	session.commit()

items = ['Shirt', 'Pants', 'Socks', 'Shoes']
for i in items:
	x = Item(name = i, category_id = 3)
	session.add(x)
	session.commit()


print "added fake data!"
