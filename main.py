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

@app.route('/chart')
def chart():
  
  return render_template("chart.html")

@app.route('/social')
def social():
  username = get_cookie('userID')
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

@app.route('/dashboard')
def dashboard():
  try:
    cursor.execute("SELECT * FROM user WHERE username = %s AND password = %s;", (request.args['usernamelogin'], request.args['passwordlogin']))
  except BaseException as e:
    print(e)
    print(cursor.statement)
  data = []
  for row in cursor:
    data.append({
      'username': row[0]
  })
  if len(data) > 0:
    return render_template('dashboard.html', usernamelogin = request.args['usernamelogin'])#, username = curUser)
  else:
    return render_template('index.html')

@app.route('/setcookie', methods = ['POST', 'GET'])
def setcookie():
  if request.method == 'POST':
    user = request.form['nm']
   
  resp = make_response(render_template('readcookie.html'))
  resp.set_cookie('userID', user)
   
  return resp