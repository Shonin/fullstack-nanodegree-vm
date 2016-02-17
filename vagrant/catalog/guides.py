# import flask
import os
from flask import Flask, render_template, request, redirect
from flask import url_for, flash, send_from_directory, abort
# from flask_bootstrap import Bootstrap

UPLOAD_FOLDER = 'uploads'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#Bootstrap(app)

# import sqlalchemy, connect to database, start session
from sqlalchemy import create_engine 
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()

import controller

# OAuth Dependencies 
from flask import session as login_session
import random, string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
  open('client_secrets.json', 'r').read())['web']['client_id']

# ======================================================
#				NOTES
# ======================================================
# You will need to perform case insensitive searches ocassionally
# Here! Take this:
# session.query(Category).filter(Category.name.ilike("electronics")).one()

# a simple if statement : if item_url is not the id of the category, if the guide id doens't 
# belong to the item, step id to guide etc then return 404

# ======================================================
#				LOGIN ROUTES
# ======================================================

@app.route('/login')
def showLogin():
  state = ''.join(random.choice(string.ascii_uppercase + string.digits)
    for x in xrange(32))
  login_session['state'] = state
  # return "the current session state is %s" %login_session['state']
  return render_template('login.html', STATE = state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    user_id = controller.getUserID(login_session['email'])
    if not user_id:
      user_id = controller.createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

    # DISCONNECT - Revoke a current user's token and reset their login_session

@app.route("/gdisconnect")
def gdisconnect():
  access_token = login_session['access_token']
  print 'In gdisconnect access token is %s', access_token
  print 'User name is: ' 
  print login_session['username']
  if access_token is None:
    print 'Access Token is None'
    response = make_response(json.dumps('Current user not connected.'), 401)
    response.headers['Content-Type'] = 'application/json'
    return response
  url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
  h = httplib2.Http()
  result = h.request(url, 'GET')[0]
  print 'result is '
  print result
  if result['status'] == '200':
    login_session.clear()
    response = make_response(json.dumps('Successfully disconnected.'), 200)
    response.headers['Content-Type'] = 'application/json'
    return response
  else:

    response = make_response(json.dumps('Failed to revoke token for given user.', 400))
    response.headers['Content-Type'] = 'application/json'
    return response

# ======================================================
#				ADMIN FUNCTIONS
# ======================================================

# def adminOnly():
# 	if 'username' not in login_session:
# 		print "\n"
# 		print "not logged in"
# 		print "\n"
# 		return abort(404)
# 	else:
# 		currentUser = controller.getUserInfo(login_session['user_id'])
# 		if currentUser.admin == 0:
# 			print "\n"
# 			print "logged in but not admin"
# 			print "\n"
# 			return abort(404)
# 		if currentUser.admin == 1:
# 			print "\n"
# 			print "welcome admin"
# 			print "\n"
# 			return "approved"

# ======================================================
#				UPLOAD ROUTES
# ======================================================

@app.route('/uploads/<filename>/')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ======================================================
#				CATEGORY ROUTES
# ======================================================
# show all categories
@app.route('/')
@app.route('/categories/')
def categories():
	return render_template('index.html', 
		categories = controller.showCategories(),
		allItems = controller.allItems(),
		admin = controller.isAdmin())

# add a new category
@app.route('/categories/new/', methods=['GET','POST'])
def newCategory():
	if controller.adminOnly() == "approved":
		if request.method == 'POST':
			filePath = controller.uploadFile(request.files['file'])
			controller.newCategory(name = request.form['name'], 
				picture = filePath)
			return redirect(url_for('categories'))
		else:
			return render_template('newcategory.html')

# edit a category
@app.route('/e/<string:category_url>/edit/', methods=['GET','POST'])
def editCategory(category_url):
	if controller.adminOnly() == "approved":
		if request.method == 'POST':
			filePath = controller.uploadFile(request.files['file'])
			controller.editCategory(category_url = category_url, 
				name = request.form['name'], 
				picture = filePath)
			return redirect(url_for('categories'))
		else:
			return render_template('editcategory.html', 
				category = controller.showCategory(category_url))

# delete a category
@app.route('/e/<string:category_url>/delete/', methods=['GET','POST'])
def deleteCategory(category_url):
	if controller.adminOnly() == "approved":
		if request.method == 'POST':
			controller.deleteCategory(category_url = category_url)
			#flash("New menu item created!")
			return redirect(url_for('categories'))
		else:
			return render_template('deletecategories.html', 
				category = controller.showCategory(category_url))

# ======================================================
#				ITEM ROUTES
# ======================================================

# view a list of a categories items
@app.route('/e/<string:category_url>/')
def items(category_url):
	return render_template('items.html', 
		category = controller.showCategory(category_url), 
		items = controller.showItems(category_url),
		allItems = controller.allItems(), 
		categories = controller.showCategories(),
		admin = controller.isAdmin())

# add a new item
@app.route('/e/<string:category_url>/new/', methods=['GET','POST'])
def newItem(category_url):
	if controller.adminOnly() == "approved":
		if request.method == 'POST':
			filePath = controller.uploadFile(request.files['file'])
			controller.newItem(category_url = category_url, 
				name = request.form['name'],
				picture = filePath)
			# flash("New item created!")
			return redirect(url_for('items', category_url = category_url))
		else:
			return render_template('newitem.html', 
				category = controller.showCategory(category_url))

# edit an item
@app.route('/e/<string:category_url>/<string:item_url>/edit/', methods=['GET','POST'])
def editItem(category_url, item_url):
	if controller.adminOnly() == "approved":
		if request.method == 'POST':
			filePath = controller.uploadFile(request.files['file'])
			controller.editItem(item_url = item_url, 
				name = request.form['name'],
				picture = filePath)
			# flash("message here!")
			return redirect(url_for('items', category_url = category_url))
		else:
			return render_template('edititem.html', 
				category = controller.showCategory(category_url), 
				item = controller.showItem(item_url))

# delete aan item
@app.route('/e/<string:category_url>/<string:item_url>/delete/', methods=['GET','POST'])
def deleteItem(category_url, item_url):
	if controller.adminOnly() == "approved":
		if request.method == 'POST':
			controller.deleteItem(item_url = item_url)
			# flash("message here!")
			return redirect(url_for('items', category_url = category_url))
		else:
			return render_template('deleteitem.html', 
				category = controller.showCategory(category_url), 
				item = controller.showItem(item_url))



# ======================================================
#				SERVER STUFF
# ======================================================

# run app on localhost 8000 with sessions and debugging enabled
if __name__ == '__main__':
	app.secret_key = 'password123'
	app.debug = True
	app.run(host = '0.0.0.0', port = 8000) 


