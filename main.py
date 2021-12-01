from flask import Flask, make_response, jsonify, request
from flask import render_template
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
<<<<<<< HEAD
  
  return render_template("chart.html")
=======
  stock = request.args['ticker']
  return make_response(render_template('chart.html', ticker = stock))

@app.route('/social')
def social():
 username = request.cookies.get("userID")
 cursor.execute("SELECT * FROM trade NATURAL JOIN user WHERE %s ORDER BY datetime", (username,)) # get my trades.
 my_trades = []
 for x in cursor:
   my_trades.append(x)
 print (my_trades)
 return render_template("social.html", mytrades=my_trades)
>>>>>>> f2b550fbc6d7a45935c1bb97bd89e32ca3f4b71a

@app.route('/social')
def social():
  username = request.cookies.get("userID")
  cursor.execute("SELECT * FROM trade NATURAL JOIN user WHERE %s ORDER BY datetime", (username,)) # get my trades.
  my_trades = []
  for x in cursor:
    my_trades.append(x)
  print (my_trades)
  return render_template("social.html", mytrades=my_trades)


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

<<<<<<< HEAD
@app.route('/dashboard', methods =  ['GET', 'POST'])
def dashboard():
  if request.method == 'POST': 
    username = request.form['usernamelogin']
    password =  request.form['passwordlogin']
  
  try:

    
    cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s;", (username, password))
=======
 
@app.route('/dashboard', methods =  ['GET', 'POST'])
def dashboard():
  if request.method == 'POST':
   username = request.form['usernamelogin']
   password =  request.form['passwordlogin']
  try:
   cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s;", (username, password))
>>>>>>> f2b550fbc6d7a45935c1bb97bd89e32ca3f4b71a
  except BaseException as e:
   print(e)
   print(cursor.statement)
  data = []
  for row in cursor:
   data.append({
     'username': row[0]
  })
  if len(data) > 0:
<<<<<<< HEAD
    resp = make_response(render_template('dashboard.html', usernamelogin = request.form['usernamelogin']))#, username = curUser))
    resp.set_cookie('userID', request.form['usernamelogin'])
   
    return resp
    
=======
   resp = make_response(render_template('dashboard.html', usernamelogin = request.form['usernamelogin']))
   resp.set_cookie('userID', request.form['usernamelogin'])
   return resp
  
  #else:
  #  try:
  #    username = request.cookies.get("userID")
  #  except BaseException as e:
  #    return render_template('index.html')
>>>>>>> f2b550fbc6d7a45935c1bb97bd89e32ca3f4b71a
  else:
   return render_template('index.html')


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