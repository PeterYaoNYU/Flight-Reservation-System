from flask import Flask, render_template, request, url_for, redirect, session
import mysql.connector

app = Flask(__name__)

conn = mysql.connector.connect(host='localhost', user='root', password='20021228Peter', database = 'flight')

@app.route('/')
def hello():
    return render_template('index.html')


@app.route('/publicinfo', methods = ['POST', 'GET'])
def publicinfo():
    if request.method == 'GET':
        return render_template('publicinfo.html')
    if request.method == 'POST':
        arrival_city = request.form.get('arrival_city')
        departure_city = request.form.get('departure_city')
        departure_date = request.form.get('departure_date')
        
        data_public = None
        cursor = conn.cursor()
        query = "select * from flight where arrive_airport = '{}' and depart_airport='{}' and date(departure_time) = '{}'"
        cursor.execute(query.format(departure_city, arrival_city, departure_date))
        data_public = cursor.fetchall()
        cursor.close() 
        print(data_public)
        return render_template("publicinfo.html", data_public = data_public)
    
@app.route('/customer_register', methods = ['POST', 'GET'])
def customer_register():
    if request.method == 'GET':
        return render_template('user_register.html')
    if request.method == 'POST':
        return
        
        