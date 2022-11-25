from flask import Flask, render_template, request, url_for, redirect, session, flash
import mysql.connector
from flask_bootstrap import Bootstrap

app = Flask(__name__)

conn = mysql.connector.connect(host='localhost', user='root', password='20021228Peter', database = 'flight')

app.secret_key="I hate expectation maximization!"

@app.route('/')
def hello():
    if 'email' in session:
        return redirect("/home")
    else:
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
    if session['role'] == 'booking_agent' and session['email']:
        return redirect("/agent_search")
    # user is not logged in
    if session['role']!='customer' or not session['email']:
        return render_template("customer_not_logged_in.html")
    # get the available cities and airport names for dropdown tables
    conn.reconnect()
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
        print(depart)
        arrive = request.form.get('arrive')
        print(arrive)
        depart_date = request.form.get('depart_date')
        print(depart_date)
        # need to make sure that we only get flights with available seats left
        # could be optimized into a procedure or a function later!!!
        purchase_query = "with avail_airplane_id as(\
            select flight_num, airplane_id, seats\
            from flight f join airplane a on(a.id = f.airplane_id)\
            where f.depart_airport = '{}' and f.arrive_airport='{}' and date(departure_time) = '{}'\
            ),\
            seats_taken as(\
            select flight_num, count(customer_email) as taken\
            from ticket natural right outer join avail_airplane_id\
            group by flight_num\
            )\
            select airline_name, flight_num, departure_time, arrival_time, price\
            from flight natural join avail_airplane_id natural join seats_taken\
            where avail_airplane_id.seats - seats_taken.taken > 0;"
        cursor = conn.cursor();
        cursor.execute(purchase_query.format(depart, arrive, depart_date))
        print(purchase_query.format(depart, arrive, depart_date))
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
        cursor.execute(max_query)
        max_ticket_id = cursor.fetchone()[0] + 1
        print(max_ticket_id)
        # get the airline name by the flight number 
        airline_name = get_airline_name(flight_num);
        # insert into the ticket table the corresponding values 
        insert_ticket_query = "insert into ticket values('{}', '{}', '{}', NULL, '{}');"
        print(insert_ticket_query.format(max_ticket_id, airline_name, flight_num, session['email']))
        
        cursor.execute(insert_ticket_query.format(max_ticket_id, airline_name, flight_num, session['email']))
        conn.commit()
        cursor.close()
        # redirect back to the homepage with a flash message(shall be implemented in the base template)
        flash("Purchase Is Complete")
        return redirect('/home')
        

            
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
            # error = "incorrect username or password"
            # error is deprecated here, use flash which is more flexible
            flash("incorrect username or password")
            return redirect(url_for('login'))
        else:
            session['role'] = role
            session['email'] = email
            return redirect('/home')
        
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
            if not start_date or not end_date:
                return redirect("/home")
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
    # if the role is an agent, the homepage will be completely different
    elif role=='booking_agent':
        return redirect("/agent_home")
    elif role=='airline_staff':
        return "under construction for airline_staff"
    
# ******************************************************************
# ******************************************************************
# Agent Functions Start Here
# ******************************************************************
# ******************************************************************

@app.route('/agent_home')
def agent_home():
    if "role" in session and session["role"]=="booking_agent":
        return render_template("agent_home.html", agent_email = session['email'])
    else:
        flash("Must Log In First Before Accessing the Booking Agent Homepage!")

@app.route("/agent_view_flight", methods = ['GET', 'POST'])
def agent_view_flight():
    # check if the agent is really logged in
    if not ("role" in session and session["role"] =="booking_agent"):
        flash("Agents: Must Log In First Before Viewing Cients' Flights")
        return redirect("/login")
    if request.method == "GET":
        # query all the upcoming flights and push them to the webpage
        agent_email = session["email"]
        upcoming_query = "select airline_name, flight_num, customer_email, ticket_id, departure_time, arrival_time, price, arrive_airport, (select city from airport a1 where a1.name=arrive_airport) as arrive_city, depart_airport, (select city from airport a2 where a2.name = depart_airport) as depart_city from ticket natural join flight where ticket.booking_agent_email='{}' and departure_time>=NOW() order by departure_time ASC;"
        cursor = conn.cursor()
        cursor.execute(upcoming_query.format(agent_email))
        upcoming_flights = cursor.fetchall()
        cursor.close()
        print(upcoming_flights)
        return render_template('agent_view_flight.html', upcoming_flights = upcoming_flights, agent_email = session['email'])
    
    
# !!!!!!!!!!!!!!!!!!!!!
# here I tried out the mysql prepared statement via the mysql-python connector
@app.route("/agent_search", methods = ["GET", "POST"])
def agent_search():
    # user is not logged in
    if session['role']!='booking_agent' or not session['email']:
        flash("Dear Booking Agent, Please Login Before Purchasing")
        return redirect("/login")
    # get the potential destinations and such
    conn.reconnect()
    cursor = conn.cursor()
    stmt = "select * from airport;"
    cursor.execute(stmt);
    airport_city = cursor.fetchall()
    cursor.close()
    print("city/airport:", airport_city)
    # get the available cities and airport names for dropdown tables
    if request.method == "GET":
        return render_template('agent_search.html', airport_city=airport_city)
    # booking agent has made a query about which flight they want to purchase
    # make the query and offer them the options to buy tickets
    elif request.method == 'POST':
        depart = request.form.get('depart')
        print(depart)
        arrive = request.form.get('arrive')
        print(arrive)
        depart_date = request.form.get('depart_date')
        print(depart_date)
        if (not depart or not arrive):
            flash("Please Enter the Departure and Arrival Airport")
            return redirect("/agent_search")
        if not depart_date:
            conn.reconnect()
            cursor = conn.cursor(prepared=True)
            agentSearchNoDate = "call agentSearchNoDate(%s, %s, %s);"
            cursor.execute(agentSearchNoDate, (depart, arrive, session['email']))
            avail_flights = cursor.fetchall()
            print(avail_flights)
            cursor.close()
            return render_template("agent_search.html", avail_flights = avail_flights, airport_city = airport_city)
        elif depart_date:
            conn.reconnect()
            cursor = conn.cursor(prepared=True)
            agentSearchWithDate = "call agentSearchWithDate(%s, %s, %s, %s);"
            cursor.execute(agentSearchWithDate, (depart, arrive, depart_date, session['email']))
            avail_flights = cursor.fetchall()
            cursor.close()
            return render_template("agent_search.html", avail_flights=avail_flights, airport_city = airport_city)
        
@app.route('/agent_purchase/<airline_name>/<flight_num>', methods = ["GET", "POST"])
def agent_purchase(airline_name, flight_num):
    if session['role'] != "booking_agent":
        flash("Dear Booking Agent, Please Login Before Purchasing")
        return redirect("/login")
    if request.method == "GET":
        # before purchase, check again if there are available flights,
        # in case the ticket is very popular and just got sold out!
        # also check if the agent really works for this airline company!!!
        conn.reconnect()
        cursor = conn.cursor(prepared= True)
        # cursor.callproc("agentPurchaseConfirm", (airline_name, flight_num, session['email']))
        # avail_flights = []
        # for result in cursor.stored_results():
        #     avail_flights = result.fetchall()
        cursor.execute("call agentPurchaseConfirm(%s, %s, %s);", (airline_name, flight_num, session['email']))
        avail_flights = cursor.fetchall()
        print(avail_flights)
        cursor.close()
        # now get customer info to decide for whom this purchas is for
        conn.reconnect()
        stmt = "select name, email from customer order by name;"
        cursor = conn.cursor()
        cursor.execute(stmt)
        customer_info = cursor.fetchall()
        print(customer_info)
        if avail_flights:
            return(render_template("agent_purchase.html", avail_flights = avail_flights, customer_info = customer_info))
        elif not avail_flights:
            return (render_template("agent_purchase.html", error = "No Flight Now"))
    elif request.method == "POST":
        customer_email = request.form.get("customer_email")
        print("PURCHASING: ", customer_email)
        conn.reconnect()
        cursor = conn.cursor(prepared=True)
        print("call agentPurchase (%s, %s, %s, %s)", airline_name, flight_num, session['email'], customer_email)
        cursor.execute("call agentPurchase (%s, %s, %s, %s);", (airline_name, flight_num, session['email'], customer_email))
        conn.commit()
        cursor.close()
        flash("Agent Puchase Success")
        return redirect("/agent_search")

        
    
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
    cursor.close()
    return name[0]

def get_airline_name(flight_num):
    cursor = conn.cursor()
    name_query = "select airline_name from flight where flight_num = '{}';"
    cursor.execute(name_query.format(flight_num))
    airline_name = cursor.fetchone()[0]
    return airline_name