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
  
  
  # cursor.execute('SELECT follows.username2, ticker, amount, trade.tid, COUNT(likes.username), COUNT(dislikes.username) FROM participates_in, trade, follows, likes, dislikes WHERE follows.username1=%s AND participates_in.tid = trade.tid AND trade.username = follows.username2 GROUP BY trade.tid;',(username,))
  for x in cursor:
    myfollowedtrade.append(x)
  # print(myfollowedtrade)
  return render_template("social.html", usernamelogin=username, myfollowed=myfollowed, myfollowedtrade=myfollowedtrade)

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
  print(request.args.get('liked'))
  try:
    liked = request.args['liked']

    cursor.execute('INSERT INTO likes VALUES(%s,%s)',(liked,username))
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

@app.route('/dashboard', methods = ['POST', 'GET'])
def dashboard():
  if not request.cookies.get("userID"):
    username = request.form['usernamelogin']
    password =  request.form['passwordlogin']
    cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s;", (username, password))
    if(len([x for x in cursor]) == 0):
      return redirect('/')
    resp = make_response(redirect("/dashboard"))
    resp.set_cookie('userID', request.form['usernamelogin'])
    return resp
  username = request.cookies["userID"]
  cursor.execute("SELECT * FROM favorites WHERE username=%s", (request.cookies["userID"],))
  favorites = [x[1] for x in cursor]
  cursor.execute("SELECT * FROM exchange")
  exchanges = sorted([(x[0], x[1], x[0] in favorites) for x in cursor], key=lambda x: 0 if x[2] else 1)
  return render_template('dashboard.html', usernamelogin = username, exchanges = exchanges) 
  
@app.route('/trade', methods = ['POST', 'GET'])
def trade():
  username = request.cookies["userID"]
  buy = request.args.get('buy')
  sell = request.args.get('sell')
  amount = request.args.get('amount')
  if(buy):
    cursor.execute('INSERT INTO trade(type,ticker,amount,username) VALUES(%s,%s,%s,%s)',(0,buy,amount,username))
  elif(sell):
    cursor.execute('INSERT INTO trade(type,ticker,amount,username) VALUES(%s,%s,%s,%s)',(1,sell,amount,username))
  else:
    pass
  return redirect('/dashboard')


@app.route('/allstocks', methods = ['POST', 'GET'])
def allstocks():
  username = request.cookies.get("userID")
  cursor.execute("SELECT max(ticker) AS ticker, ROUND(min(price), 2), ROUND(max(price), 2), max(datetime) FROM price_data WHERE ticker LIKE CONCAT(%s, '%') GROUP BY ticker;", (request.args.get('query') or "",))
  allstocks = []
  for x in cursor:
      allstocks.append(x)
  return render_template('allstocks.html', allstocks=allstocks, usernamelogin=username)

@app.route('/subscribed', methods = ['GET', 'POST'])
def subscribed():
  username = request.cookies.get("userID")
  print(request.args.get('subscribes'))
  try:
    subscribe = request.args['subscribes']
    cursor.execute('INSERT INTO subscribes_to VALUES(%s,%s)',(username, subscribe))
    mydb.commit()
  except BaseException as e:
    print (e)
    print (cursor.statement)
  return redirect('/dashboard')

@app.route('/favorite', methods = ['POST', 'GET'])
def favorite():
  username = request.cookies["userID"]
  favorite = request.args.get('favorite')
  unfavorite = request.args.get('unfavorite')
  if(favorite):
    cursor.execute('INSERT INTO favorites VALUES(%s,%s)',(username, favorite))
  elif(unfavorite):
    cursor.execute('DELETE FROM favorites WHERE username = %s AND exchange_name = %s',(username, unfavorite))
  else:
    pass
  return redirect('/dashboard')

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

@app.route('/signout', methods = ['POST', 'GET'])
def signout():
  resp = make_response(redirect('/'))
  resp.set_cookie('userID', '', expires=0)
  return resp

@app.route('/stocks')
def list_stocks():
  cursor.execute("SELECT ticker FROM is_on WHERE ticker LIKE CONCAT(%s, '%')", (request.args.get('query'),))
  return jsonify([x for x in cursor])