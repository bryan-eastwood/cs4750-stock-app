from flask import Flask, make_response, jsonify, request
from flask import render_template
from flask import redirect 
from datetime import *; from dateutil.relativedelta import *
import time

app = Flask(__name__)

import mysql.connector

mydb = mysql.connector.connect(
  host="18.191.237.169",
  user="root",
  password="cs4750",
  database="cs4750_proj"
)

cursor = mydb.cursor()

@app.route('/')
def hello():
    cursor.execute("SELECT * FROM trade NATURAL JOIN user ORDER BY datetime DESC LIMIT 5")
    trades = []
    for x in cursor:
      trades.append((x[3], "BUY" if x[2] == 0 else "SELL", x[7]))
    return render_template("index.html", top_trades=trades)

@app.route('/chart', methods =  ['GET', 'POST'])
def chart():
  stock = request.args['ticker']
  return make_response(render_template('chart.html', ticker = stock))


@app.route('/social', methods = ['POST', 'GET'])
def social():
  username = request.cookies.get("userID")
  cursor.execute("SELECT * FROM follows LEFT JOIN user on username2 = username WHERE username1 = %s ", (username,)) # get my trades.
  myfollowed = []
  for x in cursor:
    myfollowed.append(x)
  myfollowedtrade = []

  cursor.execute("SELECT * FROM likes LEFT JOIN trade on likes.tid = trade.tid WHERE likes.username = %s ", (username,)) # get my likes.

  mylikes = []
  for x in cursor:
    mylikes.append(( x[6],x[7],x[5], "BUY" if x[3] == 0 else "SELL", x[4]))
    
  print(mylikes)
  cursor.execute('SELECT * FROM (SELECT follows.username2, ticker, amount, trade.tid, COUNT(likes.username) FROM (participates_in, trade ,follows) LEFT JOIN likes ON trade.tid=likes.tid WHERE follows.username1=%s AND participates_in.tid = trade.tid AND trade.username = follows.username2 GROUP BY trade.tid) AS t1 NATURAL JOIN (SELECT follows.username2, ticker, amount, trade.tid, COUNT(dislikes.username) FROM (participates_in, trade ,follows) LEFT JOIN dislikes ON trade.tid=dislikes.tid WHERE follows.username1=%s AND participates_in.tid = trade.tid AND trade.username = follows.username2 GROUP BY trade.tid) AS t2;',(username, username))
  for x in cursor:
    myfollowedtrade.append(x)
  print(myfollowedtrade)
  return render_template("social.html", usernamelogin=username, myfollowed=myfollowed, myfollowedtrade=myfollowedtrade, mylikes=mylikes)

@app.route('/follow', methods = ['GET','POST'])
def follow():
  username = request.cookies.get("userID")
  try:
    usertofollow = request.args['usertofollow']
    cursor.execute('INSERT INTO follows VALUES(%s,%s)',(username,usertofollow))
    mydb.commit()
  except BaseException as e:
    print (e)
    print (cursor.statement)
  return redirect("/social")
@app.route('/like', methods = ['GET','POST'])
def like():
  username = request.cookies.get("userID")
  try:
    liked = request.args['liked']

    cursor.execute('INSERT INTO likes VALUES(%s,%s)',(liked,username))
    mydb.commit()
  except BaseException as e:
    print (e)
    print (cursor.statement)
  return redirect("/social")

@app.route('/dislike', methods = ['GET','POST'])
def dislike():
  username = request.cookies.get("userID")
  try:
    disliked = request.args['disliked']

    cursor.execute('INSERT INTO dislikes VALUES(%s,%s)',(disliked,username))
    mydb.commit()
  except BaseException as e:
    print (e)
    print (cursor.statement)
  return redirect("/social")

@app.route('/unfollow', methods = ['GET','POST'])
def unfollow():
  username = request.cookies.get("userID")
  print(request.args.get('usertofollow'))
  try:
    cursor.execute('DELETE FROM follows WHERE username1 = %s AND username2 = %s;', (username,request.args['unfollowed']))
    mydb.commit()
  except BaseException as e:
    print (e)
    print (cursor.statement)
  return redirect("/social")


@app.route('/data')
def data():
  latest = datetime.fromtimestamp(1628523000)
  try: 
    cursor.execute("SELECT * FROM price_data WHERE datetime > %s AND ticker = %s;", ((latest-relativedelta(days=int(request.args.get('days')))).strftime("%s"), request.args.get('ticker')))
  except BaseException as e:
    print(e)
    print(cursor.statement)
  data = []
  for row in cursor:
    data.append({
      'ticker': row[0],
      'time': row[1],
      'price': row[2],
      'vol': row[3]
    })
  return jsonify(data)

 
@app.route('/dashboard', methods =  ['GET', 'POST'])
def dashboard():

  if request.method == 'POST':
    username = request.form['usernamelogin']
    password =  request.form['passwordlogin']
  try:
    username = request.cookies.get("userID")
    return render_template('dashboard.html', usernamelogin = username) 
  except BaseException as e:
    try:
      cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s;", (username, password))
    except BaseException as e:
      print(e)
      print(cursor.statement)
    data = []
    for row in cursor:
      data.append({
      'username': row[0]
    })
    if len(data) > 0:
      resp = make_response(render_template('dashboard.html', usernamelogin = request.form['usernamelogin']))
      resp.set_cookie('userID', request.form['usernamelogin'])
      return resp
    else:
      return render_template('index.html')

@app.route('/allstocks', methods = ['POST', 'GET'])
def allstocks():
  username = request.cookies.get("userID")
  cursor.execute("SELECT max(ticker) AS ticker, ROUND(min(price), 2), ROUND(max(price), 2), max(datetime) FROM price_data GROUP BY ticker;")
  allstocks = []
  for x in cursor:
      allstocks.append(x)
  return render_template('allstocks.html', allstocks=allstocks, usernamelogin=username)

@app.route('/getcookie', methods = ['POST', 'GET'])
def getcookie():
  value = request.cookies.get('userID')   
  return jsonify(value)

@app.route('/setcookie', methods = ['POST', 'GET'])
def setcookie():   
  resp = make_response(render_template('index.html'))
  resp.set_cookie('userID', request.args.get('user'))
   
  return resp

@app.route('/newuserpage')
def newuserpage():
  cursor.execute("INSERT INTO user (username, password, first_name, last_name, likes_count) VALUES (%s, %s, %s, %s, 0);", (request.args['usernamesignup'], request.args['passwordsignup'], request.args['fnamesignup'], request.args['lnamesignup']))
  mydb.commit()
  return render_template('newuserpage.html')

@app.route('/userdeleted', methods = ['POST', 'GET'])
def userdeleted():
  username = request.cookies.get('userID')
  cursor.execute("DELETE FROM user WHERE username = %s;", (username,))
  mydb.commit()
  return render_template('userdeleted.html')

@app.route('/stocks')
def list_stocks():
  cursor.execute("SELECT ticker FROM is_on WHERE ticker LIKE CONCAT(%s, '%')", (request.args.get('query'),))
  return jsonify([x for x in cursor])