from flask import Flask, render_template, request, url_for, redirect, session, flash
import mysql.connector

app = Flask(__name__)

conn = mysql.connector.connect(host='localhost', user='root', password='20021228Peter', database = 'flight')

app.secret_key="I hate expectation maximization!"

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
        error = None;
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
            return redirect('/agent_register?error=%s' % error)
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
            
@app.route('/purchase', methods=['POST', 'GET'])
def purchase():
    # user is not logged in
    if session['role']!='customer' or not session['email']:
        return render_template("customer_not_logged_in.html")
    # get the available cities and airport names for dropdown tables
    cursor = conn.cursor()
    city_query = 'select * from airport;'
    cursor.execute(city_query)
    airport_city = cursor.fetchall()
    cursor.close()
    print(airport_city)
    # user is just trying to load the webpage
    if request.method == 'GET': 
        return render_template('purchase.html', airport_city=airport_city)
    # user has made a query about which flight they want to purchase
    # make the query and offer them the options to buy tickets
    elif request.method == 'POST':
        depart = request.form.get('depart')
        arrive = request.form.get('arrive')
        depart_date = request.form.get('depart_date')
        # need to make sure that we only get flights with available seats left
        # could be optimized into a procedure or a function later!!!
        purchase_query = "with avail_airplane_id as(\
            select flight_num, airplane_id, seats\
            from flight f join airplane a on(a.id = f.airplane_id)\
            where f.depart_airport = '{}' and f.arrive_airport='{}' and date(departure_time) = '{}'\
            ),\
            seats_taken as(\
            select flight_num, count(customer_email) as taken\
            from ticket natural join avail_airplane_id\
            group by flight_num\
            )\
            select airline_name, flight_num, departure_time, arrival_time, price\
            from flight natural join avail_airplane_id natural join seats_taken\
            where avail_airplane_id.seats - seats_taken.taken > 0;"
        cursor = conn.cursor();
        cursor.execute(purchase_query.format(depart, arrive, depart_date))
        print(purchase_query.format(depart_date, arrive, depart))
        avail_flights = cursor.fetchall();
        print(avail_flights)
        return render_template('purchase.html', airport_city = airport_city, avail_flights = avail_flights)
    
@app.route('/purchase/<flight_num>', methods = ['POST', 'GET'])
def purchase_confirm(flight_num):
    # first check if the customer is logged in or not
    if 'email' not in session:
        flash("You Will Have to Login First Before Making a Purchase", 'error')
        return redirect('/login')
    # use the parameter passed through the address to query the confirmation message
    # and provide it back to the user interface
    if request.method == 'GET':
        # find name of the customer to provide welcome
        name = findname()
        cursor = conn.cursor()
        confirmation_query = "select * from flight where flight_num = '{}';"
        cursor.execute(confirmation_query.format(flight_num))
        confirm_message = cursor.fetchone()
        cursor.close()
        print(confirm_message)
        return render_template('purchase_confirm.html', confirm_message = confirm_message, name = name)
    # the user has clicked the button, put a ticket into the db,
    # flash a message and redirect the user back to the homepage
    elif request.method == 'POST':
        cursor = conn.cursor()
        # get the unique ticket_id by finding out the current max and then plus one
        max_query = "select max(ticket_id) from ticket;"
        print(max_query)
        
        
        

            
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        role = request.form.get('roles')
        email = request.form.get('email')
        password = request.form.get('password')
        cursor=conn.cursor()
        query="select * from {} where email='{}' and password=md5('{}');"
        cursor.execute(query.format(role, email, password))
        result = cursor.fetchall()
        if not result:
            error = "incorrect username or password"
            return redirect(url_for('login', error=error))
            # return redirect(url_for('login', error=error))
        else:
            session['role'] = role
            session['email'] = email
            return redirect('/home')
        # elif role == 'agent':
        #     query="select * from booking_agent where email='{}' and password=md5('{}');"
        #     cursor.execute(query.format(email, password))
        #     result = cursor.fetchall()
        #     if not result:
        #         error = "incorrect username or password"
        #         return redirect('/login', error=error)
        #     else:
        #         session['role'] = role
        #         session['email'] = email
        #         return redirect('/home')
        # elif role == 'staff':
        #     query="select * from staff where email='{}' and password=md5('{}');"
        #     cursor.execute(query.format(email, password))
        #     result = cursor.fetchall()
        #     if not result:
        #         error = "incorrect username or password"
        #         return redirect('/login', error=error)
        #     else:
        #         session['role'] = role
        #         session['email'] = email
        #         return redirect('/home')
        
@app.route('/home', methods=['GET', 'POST'])
def home():
    role = session['role']
    email = session['email']
    cursor=conn.cursor()
    if role=='customer':
        # fetch the name of the customer so that we can greet them on their homepage
        upcoming_flights = None
        name_query = "select name from customer where email = '{}';"
        cursor.execute(name_query.format(email))
        name = cursor.fetchone()
        upcoming_query="select airline_name, flight_num, DATE_FORMAT(departure_time, '%Y.%m.%d %k:%i'), DATE_FORMAT(arrival_time, '%Y.%m.%d %k:%i'), status, arrive_airport, depart_airport from\
            flight join ticket using (airline_name, flight_num) where customer_email = '{}' and arrival_time > curtime();"
        cursor.execute(upcoming_query.format(email))
        upcoming_flights=cursor.fetchall()
        # calculate the toal money spent last year
        total_money_query = "select sum(price) as spending_last_year\
            from flight join ticket using (airline_name, flight_num)\
            where customer_email='{}' and departure_time between DATE_SUB(NOW(),INTERVAL 1 YEAR) and NOW();"
            
        cursor.execute(total_money_query.format(email))
        last_year_spending = cursor.fetchall()[0][0]
        print(last_year_spending)
        
        # if the method is get, calculate the money spent in the last 6 months
        if request.method == 'GET':
            spending_query="select sum(price) as spending, year(departure_time) as year, month(departure_time) as month\
                from flight join ticket using (airline_name, flight_num)\
                where customer_email='{}' and departure_time between DATE_SUB(NOW(), INTERVAL 6 MONTH) and NOW()\
                group by year(departure_time), month(departure_time);"
            cursor.execute(spending_query.format(email))
            spend_stat = cursor.fetchall()
            chartdata = []
            for row in spend_stat:
                chartdata.append([(str(row[1]) + '-'+str(row[2])), float(row[0])])
            print(chartdata)
            cursor.close()
            
            return render_template('/home.html', role = role, upcoming_flights = upcoming_flights, name=name[0],\
                last_year_spending = last_year_spending, chartdata=chartdata)
        # else if the method is POST, get the money spent in the specified time range
        elif request.method == 'POST':
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            spending_query="select sum(price) as spending, year(departure_time) as year, month(departure_time) as month\
                from flight join ticket using (airline_name, flight_num)\
                where customer_email='{}' and departure_time between '{}' and '{}'\
                group by year(departure_time), month(departure_time);"
            print(spending_query.format(email, start_date, end_date))
            cursor.execute(spending_query.format(email, start_date, end_date))
            spend_stat = cursor.fetchall()
            chartdata = []
            for row in spend_stat:
                chartdata.append([(str(row[1]) + '-'+str(row[2])), float(row[0])])
            print(chartdata)
            cursor.close()
            return render_template('/home.html', role = role, upcoming_flights = upcoming_flights, name=name[0],\
                last_year_spending = last_year_spending, chartdata=chartdata)
    elif role=='booking_agent':
        return "Under Construction for booking agent"
    elif role=='airline_staff':
        return "under construction for airline_staff"
    
@app.route('/logout')
def logout():
    session.pop('role')
    session.pop('email')
    return redirect('/login')

def findname():
    cursor = conn.cursor()
    name_query = "select name from customer where email = '{}';"
    cursor.execute(name_query.format(session['email']))
    name = cursor.fetchone()
    return name[0]