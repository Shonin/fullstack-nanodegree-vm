from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Item
engine = create_engine('sqlite:///inventory.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

import requests

items = session.query(Item).all()

for sku in items:
	r = requests.post("http://inerdzparts.com/quickshopping/index/checkskucart/", data = {"code":sku.sku,"name":"1"})
	response = r.text.split('mst1')
	name = response[6]
	qty = response[5]
	x = session.query(Item).filter_by(sku = sku.sku).one()
	x.qty = qty
	x.name = name
	session.add(x)
	session.commit()

def add(sku):
	x = Item(sku = sku)
	session.add(x)
	session.commit()