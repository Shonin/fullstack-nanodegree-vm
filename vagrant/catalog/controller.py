from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from werkzeug import secure_filename
import os
from flask import Flask, abort, Markup
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
import markdown

# ======================================================
#				LOGIN FUNCTIONS
# ======================================================
from flask import session as login_session

def createUser(login_session):
  newUser = User(name=login_session['username'], email=login_session[
                 'email'], picture=login_session['picture'])
  session.add(newUser)
  session.commit()
  user = session.query(User).filter_by(email=login_session['email']).one()
  return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
  try:
    user = session.query(User).filter_by(email=email).one()
    return user.id
  except:
    return None

def isAdmin():
	if login_session['user_id'] == None:
		print "\n"
		print "not logged in"
		print "\n"
		return None
	else:
		currentUser = getUserInfo(login_session['user_id'])
		if currentUser.admin == 0:
			print "\n"
			print "logged in but not admin"
			print "\n"
			return None
		if currentUser.admin == 1:
			print "\n"
			print "welcome admin"
			print "\n"
			return 1

def adminOnly():
	if 'username' not in login_session:
		print "\n"
		print "not logged in"
		print "\n"
		return abort(404)
	else:
		currentUser = getUserInfo(login_session['user_id'])
		if currentUser.admin == 0:
			print "\n"
			print "logged in but not admin"
			print "\n"
			return abort(404)
		if currentUser.admin == 1:
			print "\n"
			print "welcome admin"
			print "\n"
			return "approved"

# ======================================================
#				UPLOAD FUNCTIONS
# ======================================================
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg'])

def allowedFile(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def uploadFile(file):
	if file and allowedFile(file.filename):
		filename = secure_filename(file.filename)
		filePath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
		file.save(filePath)
		filePath = "/" + filePath
		return filePath

# def getPath(file):
# 	if file and allowedFile(file.filename):
# 			filename = secure_filename(file.filename)
# 			filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
# 			return filepath

# ======================================================
#				TEMPLATE FUNCTIONS
# ======================================================

def allItems():
	allItems = session.query(Item).all()
	return allItems

# ======================================================
#				CATEGORY FUNCTIONS
# ======================================================

def showCategories():
	categories = session.query(Category).all()
	return categories

def showCategory(category_url):
	category = session.query(Category).filter(Category.name.ilike(category_url)).one()
	return category

def newCategory(name, picture):
	newCategory = Category(name = name, 
		picture = picture,
		description = description)
	session.add(newCategory)
	session.commit()

def editCategory(category_url, name, picture):
	editCategory = showCategory(category_url)
	if name:
		editCategory.name = name
	if picture:
		editCategory.picture = picture
	if description:
		editCategory.description = description
	session.add(editCategory)
	session.commit()

def deleteCategory(category_url):
	session.delete(showCategory(category_url))
	session.commit()

# ======================================================
#				ITEM FUNCTIONS
# ======================================================

def showItems(category_url):
	items = session.query(Item).filter_by(category_id = showCategory(category_url).id)
	return items

def showItem(item_url):
	item = session.query(Item).filter(Item.name.ilike(item_url)).one()
	return item

def newItem(category_url, name, picture):
	newItem = Item(name = name, 
		category_id = showCategory(category_url).id,
		picture = picture,
		description = description)
	session.add(newItem)
	session.commit()

def editItem(item_url, name, picture):
	editItem = showItem(item_url)
	if name:
		editItem.name = name
	if picture:
		editItem.picture = picture
	if description:
		editItem.description = description
	session.add(editItem)
	session.commit()

def deleteItem(item_url):
	session.delete(showItem(item_url))
	session.commit()

