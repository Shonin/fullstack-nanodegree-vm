#
# Database access functions for the web forum.
# 

import time
import psycopg2
import bleach


## Database connection


## Get posts from database.
def GetAllPosts():
  DB = psycopg2.connect("dbname=forum")
  c = DB.cursor()
  c.execute("SELECT time, content FROM posts ORDER BY time DESC")
  posts = c.fetchall()
  DB.close()
  return posts

## Add a post to the database.
def AddPost(content):
  DB = psycopg2.connect("dbname=forum")
  c = DB.cursor()
  cleaned_content = bleach.clean(content)
  c.execute("INSERT INTO posts (content) VALUES (%s)", (cleaned_content,))
  DB.commit()
  DB.close()
