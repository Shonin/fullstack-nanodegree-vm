import sys
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Date, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

Base = declarative_base()

class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key = True)
	name = Column(String)
	sku = Column(String)
	qty = Column(String)

engine = create_engine('sqlite:///inventory.db')

Base.metadata.create_all(engine)

