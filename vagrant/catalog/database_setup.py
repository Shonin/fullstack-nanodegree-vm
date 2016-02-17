import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime

Base = declarative_base()

class User(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  admin = Column(Integer, default = 0)
  name = Column(String(250))
  email = Column(String(250))
  picture = Column(String(500))

class Category(Base):
	__tablename__ = 'category'
	id = Column(Integer, primary_key = True)
	items = relationship("Item", cascade="all, delete-orphan")
	name = Column(String(50), nullable = False)
	picture = Column(String)
	description = Column(String)


class Item(Base):
	__tablename__ = 'item'
	id = Column(Integer, primary_key = True)
	category_id = Column(Integer, ForeignKey('category.id'))
	name = Column(String(50), nullable = False)
	picture = Column(String)
	description = Column(String)



engine = create_engine('sqlite:///catalog.db')
Base.metadata.create_all(engine)

