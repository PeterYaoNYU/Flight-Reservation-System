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
    
@app.route('/agent_register', methods=['POST', 'GET'])
def agent_register():
    if request.method == 'GET':
        return render_template('agent_register.html')
    if request.method == 'POST':
        email=request.form.get('email')
        password=request.form.get('password')
        booking_agent_id = request.form.get('booking_agent_id')
        cursor=conn.cursor()
        check_query="select email from booking_agent where email = '{}';"
        cursor.execute(check_query.format(email))
        existed_user = cursor.fetchall()
        cursor.close()
        if (existed_user):
            error = 'Agent Exists'
            return redirect('/agent_register')
        else:
            cursor = conn.cursor()
            insert_query = "insert into booking_agent values ('{}', md5('{}'), {});"
            cursor.execute(insert_query.format(email, password, booking_agent_id));
            conn.commit()
            cursor.close()
            print('done inserting')
            return redirect('/publicinfo')
        
    
@app.route('/customer_register', methods = ['POST', 'GET'])
def customer_register():
    if request.method == 'GET':
        return render_template('user_register.html')
    if request.method == 'POST':
        email=request.form.get('email')
        check_exist_query="select email from customer where email = '{}'"
        cursor= conn.cursor()
        cursor.execute(check_exist_query.format(email))
        existed_user = cursor.fetchone()
        if (existed_user):
            error = 'Customer Already Exists'
            cursor.close()
            render_template('user_register.html', error=error)
        else:
            name=request.form.get('name')
            password=request.form.get('password')
            building_number=request.form.get('building_number')
            street=request.form.get('streer')
            city = request.form.get('city')
            state=request.form.get('state')
            phone_number=request.form.get('phone_number')
            passport_number=request.form.get('passport_number')
            passport_expiration=request.form.get('passport_expiration')
            passport_country=request.form.get('passport_country')
            date_of_birth=request.form.get('date_of_birth')
            insert_query = "insert into customer values '{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}'"
            cursor.execute(insert_query.format(name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
            cursor.close()
            
            
            
        
        