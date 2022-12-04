from flask import Flask, render_template, request, url_for, redirect, session, flash
import mysql.connector
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField, IntegerField, PasswordField, EmailField, ValidationError
from wtforms.validators import DataRequired, Email, NumberRange, InputRequired

app = Flask(__name__)

conn = mysql.connector.connect(host='localhost', user='root', password='20021228Peter', database = 'flight')

app.secret_key="I hate expectation maximization!"
app.config['SECRET_KEY'] = "I hate expectation maximization!"
bootstrap = Bootstrap(app)

@app.route('/')
def hello():
    if 'email' in session:
        return redirect("/home")
    else:
        return render_template('index.html')
    
@app.route("/register")
def register():
    return render_template("register.html")

# enforece the length requirement
# a validator for the form
# easily reusable 
def length(min=-1, max=-1):
    message = 'Must be between %d and %d characters long.' % (min, max)

    def _length(form, field):
        l = field.data and len(field.data) or 0
        if l < min or max != -1 and l > max:
            raise ValidationError(message)

    return _length

# used in the registration process
# return true if there is already duplicate in the database
# return false if the entry is unique and new 
def check_duplicate(role, pk):
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call check_duplicate(%s, %s);", (role, pk))
    result = cursor.fetchall()
    cursor.close()
    print(result)
    if len(result) > 0:
        return True
    else:
        return False

@app.route('/publicinfo', methods = ['POST', 'GET'])
def publicinfo():
    if request.method == 'GET':
        return render_template('publicinfo.html')
    if request.method == 'POST':
        arrival_city = request.form.get('arrival_city')
        departure_city = request.form.get('departure_city')
        departure_date = request.form.get('departure_date')
        data_public = None
        conn.reconnect()
        cursor = conn.cursor()
        query = "select * from flight where arrive_airport = '{}' and depart_airport='{}' and date(departure_time) = '{}'"
        cursor.execute(query.format(departure_city, arrival_city, departure_date))
        data_public = cursor.fetchall()
        cursor.close() 
        print(data_public)
        return render_template("publicinfo.html", data_public = data_public)
    
class AgentRegisterForm(FlaskForm):
    email = EmailField("Email", validators=[InputRequired(),])
    password = PasswordField("Password", validators=[InputRequired(), ])
    booking_agent_id = IntegerField("Booking Agent ID", validators=[InputRequired(),])
    submit = SubmitField("Submit", render_kw = {'style': 'margin: 20px;'})

@app.route('/agent_register', methods=['POST', 'GET'])
def agent_register():
    form = AgentRegisterForm()
    if request.method == 'GET':
        error = None;
        return render_template('agent_register.html', form = form)
    if request.method == 'POST':
        email=form.email.data
        password=form.password.data
        booking_agent_id = form.booking_agent_id.data
        cursor=conn.cursor()
        check_query="select email from booking_agent where email = '{}';"
        cursor.execute(check_query.format(email))
        existed_user = cursor.fetchall()
        cursor.close()
        if (existed_user):
            error = 'Agent Exists'
            flash("Agent Already Exists")
            return redirect('/agent_register')
        else:
            conn.reconnect()
            cursor = conn.cursor()
            insert_query = "insert into booking_agent values ('{}', md5('{}'), {});"
            cursor.execute(insert_query.format(email, password, booking_agent_id));
            conn.commit()
            cursor.close()
            print('done inserting')
            return redirect('/login')
        
class CustomerRegistrationForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    building_number = IntegerField("Building Number", validators=[DataRequired()])
    street = StringField("Street Name", validators=[DataRequired()])
    city = StringField("City", validators=[DataRequired()])
    state = StringField("State/Province", validators=[DataRequired()])
    phone_number = IntegerField("Phone Number", validators=[DataRequired()])
    passport_number = StringField("Passport Number", validators=[DataRequired()])
    passport_expiration = DateField("Passport Expiration", validators= [DataRequired()])
    passport_country = StringField("Passport Country", validators=[DataRequired()])
    date_of_birth = DateField("Date Of Birth", validators=[DataRequired()])
    submit = SubmitField("Submit")
        
# USE WTFORMS TO futher enhance the validation process
class StaffRegisterForm(FlaskForm):
    def get_airlines():
        stmt ="select * from airline;"
        conn.reconnect()
        cursor = conn.cursor()
        cursor.execute(stmt)
        airlines = cursor.fetchall()
        for i in range(len(airlines)):
            airlines[i] = (airlines[i][0], airlines[i][0])
        print(airlines)
        cursor.close()
        return airlines
    user_name = StringField("Username (HAS TO BE UNIQUE)", validators=[DataRequired()])
    password = PasswordField("Simple Password is Enough", validators=[DataRequired()])
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    date_of_birth = DateField("Date Of Birth", validators=[DataRequired()])
    airline_name = SelectField("Airline You Work For", choices=get_airlines(), validators=[DataRequired()])
    submit = SubmitField("Submit")
        
@app.route("/staff_register", methods = ["GET", "POST"])
def staff_register():
    form = StaffRegisterForm()
    if request.method == "GET":
        return render_template("staff_register.html", form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            user_name = form.user_name.data
            form.user_name.data = ''
            password = form.password.data
            form.password.data = ''
            first_name = form.first_name.data
            form.first_name.data = ''
            last_name = form.last_name.data
            form.last_name.data = ''
            date_of_birth = form.date_of_birth.data
            form.date_of_birth.data = ''
            airline_name = form.airline_name.data
            form.airline_name.data = ''
        if check_duplicate("airline_staff", user_name):
            flash("Staff Already Existes!")
            return redirect("/register")
        conn.reconnect()
        cursor = conn.cursor(prepared=True)
        cursor.execute("call insert_new_staff(%s,%s,%s,%s,%s,%s);", (user_name, password, first_name, last_name, date_of_birth, airline_name))
        conn.commit()
        cursor.close()
        return redirect("/login")
    
        
    
@app.route('/customer_register', methods = ['POST', 'GET'])
def customer_register():
    form = CustomerRegistrationForm()
    if request.method == "GET":
        return render_template("customer_register.html", form = form)
    if request.method =="POST":
        if form.validate_on_submit():
            email = form.email.data
            name = form.name.data
            password = form.password.data
            building_number = form.building_number.data
            street = form.street.data
            city = form.city.data
            state = form.state.data
            phone_number = form.phone_number.data
            passport_number = form.passport_number.data
            passport_expiration = form.passport_expiration.data
            passport_country = form.passport_country.data
            date_of_birth = form.date_of_birth.data
        # use the helper function to check if there is duplicate in the db 
        if check_duplicate("customer", email):
            # there is indeed duplicate customer 
            flash("Customer Already Existing!")
            return redirect("/register")
        conn.reconnect()
        cursor = conn.cursor(prepared=True)
        cursor.execute("insert into customer values (%s,%s,md5(%s),%s,%s,%s,%s,%s,%s,%s,%s,%s);", (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth))
        conn.commit()
        flash("Registration Complete")
        return redirect("/login")
    
            
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
        conn.reconnect()
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
        conn.reconnect()
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
        conn.reconnect()
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
        conn.reconnect()
        cursor=conn.cursor()
        if role != "airline_staff":
            query="select * from {} where email='{}' and password=md5('{}');"
        else:
            query = "select * from {} where username='{}' and password=md5('{}');"
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
    if "role" not in session:
        flash("login first")
        return redirect("/login")
    role = session['role']
    email = session['email']
    conn.reconnect()
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
        return redirect("/staff_home")
    
# ******************************************************************
# ******************************************************************
# Agent Functions Start Here
# prepared statements used!
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
        conn.reconnect()
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
    
    
# USE WTFORMS TO futher enhance the validation process
class CommissionForm(FlaskForm):
    start_date = DateField("Search the Commission From This Date Backward", validators=[DataRequired()])
    date_range = IntegerField("Number of Dates to Query", validators=[DataRequired(), NumberRange(min=0, max=365)])
    submit = SubmitField("Submit")
    

def db_get_commission(start_date, date_range):
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    print(session['email'])
    if start_date!="date(now())":
        cursor.execute("call viewMyCommissionNotDefault(%s, %s, %s, @totalAmount, @averageCommission, @totalTicket)", (session['email'], start_date, date_range))
    else:
        cursor.execute("call viewMyCommissionNotDefault(%s, date(now()), 30, @totalAmount, @averageCommission, @totalTicket)", (session['email'],))
    cursor.execute("select @totalAmount;")
    total_amount = cursor.fetchone()[0]
    if total_amount != None:
        total_amount = float(total_amount)
    else:
        total_amount = 0
        
    cursor.execute("select @averageCommission;")
    average_commission = cursor.fetchone()[0]
    if average_commission != None:
        average_commission = float(average_commission)
    else:
        average_commission = 0
    cursor.execute("select @totalTicket;")
    total_ticket = cursor.fetchone()[0]
    if total_ticket != None:
        total_ticket = int(total_ticket)
    else:
        total_ticket = 0
    print(total_amount, average_commission, total_ticket)
    cursor.close()
    return tuple([total_amount, average_commission, total_ticket])

@app.route("/agent_commission", methods = ["GET", "POST"])
def agent_commission():
    if session['role'] != "booking_agent" or not session['email']:
        flash("Have to Login First as a Booking Agent")
        return redirect("/login")
    form = CommissionForm()
    if request.method == "GET":
        total_amount, average_commission, total_ticket = db_get_commission("date(now())", 30)
        return render_template("agent_commission.html", total_amount = total_amount, average_commission = average_commission, total_ticket = total_ticket, form = form)
    elif request.method == "POST":
        if form.validate_on_submit():
            start_date = form.start_date.data
            print(type(start_date), start_date)
            date_range = form.date_range.data
            print(type(date_range), date_range)
        total_amount, average_commission, total_ticket = db_get_commission(start_date, date_range)
        return render_template("agent_commission.html", total_amount = total_amount, average_commission = average_commission, total_ticket = total_ticket, form = form)
    
    
@app.route("/agent_top_customers", methods = ["GET",])
def agent_top_customers():
    if session['role'] != "booking_agent":
        flash("Must Login As a Booking Agent")
        return redirect("/login")
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call top_five_ticket_count(%s);", (session['email'], ))
    based_on_ticket = cursor.fetchall()
    conn.reconnect()
    cursor.execute("call top_five_commission_last_year(%s);", (session['email'], ))
    based_on_money = cursor.fetchall()
    print(based_on_ticket)
    print(based_on_money)
    return render_template("agent_top_customers.html", based_on_ticket = based_on_ticket, based_on_money = based_on_money)

# ******************************************************************
# ******************************************************************
# Airline Staff View Functions Start Here
# ******************************************************************
# ******************************************************************
def check_staff_validity():
    if "role" in session and session["role"] == "airline_staff":
        return True
    else:
        return False

def get_airport_city():
    stmt = "select * from airport;"
    conn.reconnect()
    cursor = conn.cursor()
    cursor.execute(stmt)
    airport_city = cursor.fetchall()
    cursor.close()
    return airport_city

def get_staff_airline():
    stmt = "select airline_name from airline_staff where username = %s;"
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute(stmt, (session["email"], ))
    airline_name = cursor.fetchone()
    print(airline_name)
    cursor.close()
    return airline_name[0]

# ******************************************************************
# view reports (all)
# ******************************************************************
class StaffViewReport:
    start_date = DateField("Start Date", validators=[DataRequired(),])
    end_date = DateField("End Date", validators=[DataRequired(), ])
    submit = SubmitField("Submit",  render_kw = {'style': 'margin: 20px;'})


@app.route("/view_report", methods = ["GET", "POST"])
def view_report():
    # first check if the user is authorized to do this!
    if not check_staff_validity():
        flash("Only Staff Can Access")
        return redirect("/login")
    airline_name = get_staff_airline()
    form = StaffViewReport()
    if request.method == "GET":
        return render_template("staff_view_report.html", form = form, airline_name = airline_name)
    # if request.method == "POST":
    #     conn.reconnect()
    #     cursor = conn.cursor(prepared=True)
    #     cursor.execute("call ") 



# ******************************************************************
# comparison of revenue earned (all)
# ******************************************************************
@app.route("/comparison_of_revenue", methods=["GET", "POST"])
def comparison_of_revenue():
    # first check if the user is authorized to do this!
    if not check_staff_validity():
        flash("Only Staff Can Access")
        return redirect("/login")
    airline_name = get_staff_airline()
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call comparisonRevenueEarned(%s, @directSalesMonth, @directSalesYear, @totalSalesMonth, @totalSalesYear);", (airline_name, ))
    cursor.execute("select @directSalesMonth;")
    directSalesMonth = cursor.fetchone()[0]
    cursor.execute("select @directSalesYear;")
    directSalesYear = cursor.fetchone()[0]
    cursor.execute("select @totalSalesMonth;")
    totalSalesMonth = cursor.fetchone()[0]
    cursor.execute("select @totalSalesYear;")
    totalSalesYear = cursor.fetchone()[0]
    indirectSalesMonth = totalSalesMonth - directSalesMonth
    indirectSalesYear  = totalSalesYear - directSalesYear
    return render_template("comparison_of_revenue.html", airline_name=airline_name, data1=[['Direct Sales Last Month', directSalesMonth], ["Indirect Sales Last Month", indirectSalesMonth]], 
                           data3 = [['Direct Sales Last Year', directSalesYear], ["Indirect Sales Last Year", indirectSalesYear]])

    
    
        


# ******************************************************************
# grant new permissions(admin)
# ******************************************************************
# get all staff that works for this airline
def get_all_staff(airline_name):
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call get_all_staff(%s);" , (airline_name, ))
    result = cursor.fetchall()
    cursor.close()
    return result

# get all possible permissions
def get_all_permission():
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call get_all_permission();")
    result = cursor.fetchall()
    cursor.close()
    return result

@app.route("/grant_new_permission", methods=["GET", "POST"])
def grant_new_permission():
    # first check if the user is authorized to do this!
    if not check_staff_validity():
        flash("Only Staff Can Access")
        return redirect("/login")
    # make sure the person accessing this page has admin permission
    if not check_staff_role("admin"):
        flash("Only Admin Has Permission to Change Status")
        return redirect("/home")
    airline_name = get_staff_airline()
    all_staff = get_all_staff(airline_name)
    all_permission = get_all_permission()
    if request.method== "GET":
        return render_template("grant_new_permission.html", airline_name=airline_name, all_staff = all_staff, all_permission = all_permission)
    elif request.method == "POST":
        staff = request.form.get("staff")
        permission = request.form.get("permission")
        conn.reconnect()
        cursor = conn.cursor(prepared=True)
        cursor.execute("call grant_new_permission(%s, %s);", (staff, permission))
        conn.commit()
        cursor.close()
        flash("Successfullt Inserted New Permission")
        return redirect("/grant_new_permission")
    
    
    

# ******************************************************************
# check top destinations (all)
# ******************************************************************
@app.route("/view_top_destinations")
def view_top_destinations():
    # first check if the user is authorized to do this!
    if not check_staff_validity():
        flash("Only Staff Can Access")
        return redirect("/login")
    airline_name = get_staff_airline()
    
    # fetch the three most popular destinations in the past 3 months
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call top_destination_3_month(%s);", (airline_name,))
    three_month = cursor.fetchall()
    cursor.close()
    
    # fetch the three most popular destinations in the last year
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call top_destination_1_year(%s);", (airline_name,))
    one_year = cursor.fetchall()
    cursor.close()
    
    # render the template with the info 
    return render_template("view_top_destinations.html", three_month = three_month, one_year = one_year)

# ******************************************************************
# check frequent customers (all)
# ************************n******************************************    
@app.route("/view_frequent_customer", methods = ["GET", "POST"])
@app.route("/view_frequent_customer/<customer_email>", methods = ["GET", "POST"])
def view_frequent_customer(customer_email = None):
    # first check if the user is authorized to do this!
    if not check_staff_validity():
        flash("Only Staff Can Access")
        return redirect("/login")
    airline_name = get_staff_airline()
    # fetch the list of frequent customers 
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call frequent_customer (%s);", (airline_name, ))
    frequent_customer = cursor.fetchall()
    cursor.close()
    # render the template
    if request.method == "GET" and customer_email:
        conn.reconnect()
        cursor = conn.cursor(prepared=True)
        cursor.execute("call all_flights_taken (%s, %s);", (customer_email, airline_name))
        all_flights = cursor.fetchall()
        cursor.close()
        return render_template("view_frequent_customer.html", airline_name = airline_name, frequent_customer = frequent_customer, all_flights=all_flights)
    if request.method == "GET":
        return render_template("view_frequent_customer.html", airline_name = airline_name, frequent_customer = frequent_customer)


# ******************************************************************
# Add New Booking Agent (admin)
# ******************************************************************
def get_avail_booking_agent(airline_name):
    stmt = "call avail_booking_agent(%s);"
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute(stmt, (airline_name,))
    result = cursor.fetchall()
    return result

@app.route("/add_booking_agent", methods = ["GET", "POST"])
def add_booking_agent():
    # first check if the user is authorized to do this!
    if not check_staff_validity():
        flash("Only Staff Can Access")
        return redirect("/login")
    # make sure the person accessing this page has admin permission
    if not check_staff_role("admin"):
        flash("Only Admin Has Permission to Change Status")
        return redirect("/home")
    airline_name = get_staff_airline()
    avail_booking_agent = get_avail_booking_agent(airline_name)
    if request.method== "GET":
        return render_template("add_booking_agent.html", airline_name = airline_name, avail_booking_agent = avail_booking_agent)
    elif request.method=="POST":
        agent_email = request.form.get("avail_booking_agent")
        print(agent_email)
        conn.reconnect()
        cursor = conn.cursor(prepared=True)
        cursor.execute("insert into works_for values(%s, %s);", (airline_name, agent_email))
        conn.commit()
        flash("New Agent Added")
        return redirect("/add_booking_agent")

# ******************************************************************
# view top 5 booking agents (all staff)
# ******************************************************************
@app.route("/view_booking_agent")
def view_booking_agent():
    # first check if the user is authorized to do this!
    if not check_staff_validity():
        flash("Only Staff Can Access")
        return redirect("/login")
    airline_name = get_staff_airline()
    stmt = "call staff_view_booking_agent(%s, %s, %s);"
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    # get the top 5 agents based on the number of tickets sold last year
    cursor.execute(stmt, (airline_name, "ticket", "year"))
    agents_ticket_year = cursor.fetchall()
    cursor.close()
    # get the top 5 agents based on the number of tickets sold last month
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute(stmt, (airline_name, "ticket", "month"))
    agents_ticket_month = cursor.fetchall()
    print(agents_ticket_month)
    cursor.close()
    # get the top 5 agents based on the number of tickets sold last month
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute(stmt, (airline_name, "amount", "year"))
    agents_amount_year = cursor.fetchall()
    cursor.close()
    # render the results
    return render_template("view_booking_agent.html", agents_ticket_month = agents_ticket_month, agents_ticket_year=agents_ticket_year, agents_amount_year = agents_amount_year)
  


# ******************************************************************
# Add New Airplane (admin)
# ******************************************************************

class NewAirplaneForm(FlaskForm):
    id = IntegerField("ID of the New Airplane (Duplicate ID Will Be Rejected", validators=[DataRequired(), ])
    seats = IntegerField("Seats on the Airplane", validators=[DataRequired(), ])
    submit = SubmitField("Submit", render_kw = {'style': 'margin: 20px;'})
    
# return true if there is duplicate flight, false otherwise
def check_duplicate_plane(airline_name, plane_id):
    id = None
    stmt = "call check_duplicate_airplane(%s, %s);"
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute(stmt, (airline_name, plane_id))
    id = cursor.fetchall()
    print(id)
    cursor.close()
    if id:
        return True
    elif not id:
        return False

@app.route("/add_airplane", methods = ["GET", "POST"])
def add_airplane():
    # first check if the user is authorized to do this!
    if not check_staff_validity():
        flash("Only Staff Can Access")
        return redirect("/login")
    # make sure the person accessing this page has admin permission
    if not check_staff_role("admin"):
        flash("Only Admin Has Permission to Change Status")
        return redirect("/home")
    airline_name = get_staff_airline()
    airplane = get_airline_airplane(airline_name)
    form = NewAirplaneForm()
    if request.method == "GET":
        return render_template("add_airplane.html", airline_name = airline_name, airplane = airplane, form = form)
    if request.method == "POST":
        if form.validate_on_submit():
            new_id = form.id.data
            new_seats = form.seats.data
            if check_duplicate_plane(airline_name, new_id):
                flash("This Plane Already Exists")
                return redirect("/add_airplane")
            else:
                stmt = "insert into airplane values(%s, %s, %s);"
                conn.reconnect()
                cursor = conn.cursor(prepared=True)
                cursor.execute(stmt, (airline_name, new_id, new_seats))
                conn.commit()
                cursor.close()
                flash("Successfully Add New Airplanes")
                return redirect("/add_airplane")
        return redirect("/add_airplane")
    

            

@app.route('/staff_home', methods = ["GET", ])
def staff_home():
    if "role" in session and session["role"]=="airline_staff":
        return render_template("staff_home.html", staff_email = session['email'])
    else:
        flash("Must Log In First Before Accessing the Staff Homepage!")
        return redirect("/login")
    
@app.route('/staff_view_flights', methods =["GET", "POST"])
def staff_view_flights():
    if not check_staff_validity():
        flash("Please Login First")
        return redirect("/login")
    airline_name = get_staff_airline()
    airport_city = get_airport_city()
    if request.method == "GET":
        conn.reconnect()
        cursor = conn.cursor(prepared=True)
        cursor.execute("call staff_view_flights_default(%s);", (airline_name, ))
        upcoming = cursor.fetchall()
        cursor.close()
        print(upcoming)
        return render_template("staff_view_flights.html", upcoming = upcoming, username = session["email"], airport_city = airport_city)
    elif request.method == "POST":
        source_city = request.form.get("depart")
        destination_city = request.form.get("arrive")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        if source_city and destination_city and start_date and end_date:
            conn.reconnect()
            cursor = conn.cursor(prepared=True)
            cursor.execute("call staff_view_flights_date_city(%s, %s, %s, %s, %s);", (airline_name,start_date, end_date, source_city, destination_city))
            upcoming = cursor.fetchall()
            cursor.close()
            print(upcoming)
            return render_template("staff_view_flights.html", upcoming = upcoming, username = session["email"], airport_city = airport_city)
        elif source_city and destination_city:
            conn.reconnect()
            cursor = conn.cursor(prepared=True)
            cursor.execute("call staff_view_flights_city(%s, %s, %s);", (airline_name,source_city, destination_city))
            upcoming = cursor.fetchall()
            cursor.close()
            print(upcoming)
            return render_template("staff_view_flights.html", upcoming = upcoming, username = session["email"], airport_city = airport_city)
        elif start_date and end_date:
            conn.reconnect()
            cursor = conn.cursor(prepared=True)
            cursor.execute("call staff_view_flights_date(%s, %s, %s);", (airline_name,start_date, end_date))
            upcoming = cursor.fetchall()
            cursor.close()
            print(upcoming)
            return render_template("staff_view_flights.html", upcoming = upcoming, username = session["email"], airport_city = airport_city)
        else:
            return redirect('/staff_view_flights')
        
# check if the staff role matches the expectation 
def check_staff_role(role):
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call check_staff_role(%s, %s);", (session['email'], "admin"))
    result = cursor.fetchall()
    print(result)
    if len(result) == 0:
        return False
    else:
        return True
    
def get_airline_airplane(airline_name):
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call get_airline_airplane(%s);", (airline_name, ))
    result = cursor.fetchall()
    cursor.close()
    return result

# check if there is already duplicate flight in the db
# return true if there is duplicate 
# return false otherwise
def check_duplicate_flight(airline_name, flight_num):
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call check_duplicate_flight(%s, %s);", (airline_name, flight_num))
    result = cursor.fetchall()
    if result:
        return True
    else:
        return False
    
def get_flight_num(airline_name):
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    stmt = "select flight_num from flight where airline_name = %s;"
    cursor.execute(stmt, (airline_name, ))
    result = cursor.fetchall()
    cursor.close()
    print(result)
    return result
   
@app.route("/change_status", methods = ["GET", "POST"])
def change_flight_status():
    if not check_staff_validity():
        flash("Only Staff Can Access")
        return redirect("/login")
    # make sure the person accessing this page has operator permission
    if not check_staff_role("operator"):
        flash("Only Operator Has Permission to Change Status")
        return redirect("/home")
    airline_name = get_staff_airline()
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call staff_view_flights_date(%s, %s, %s);", (airline_name, "1999-01-01", "2999-01-01"))
    all_flights = cursor.fetchall()
    cursor.close()
    print(all_flights)
    flight_numbers = get_flight_num(airline_name)
    if request.method == "GET":
        return render_template("change_status.html", all_flights = all_flights, flight_numbers = flight_numbers)
    elif request.method == "POST":
        flight_num_to_update = request.form.get("flight_num")
        new_status = request.form.get("status")
        conn.reconnect()
        cursor = conn.cursor(prepared=True)
        cursor.execute("call update_flight_status(%s, %s, %s);", (airline_name, flight_num_to_update,new_status))
        conn.commit()
        cursor.close()
        flash("Status Update Success")
        return redirect("/change_status")
    
# this function allows staff with admin permit to add new flights to the system
# !!!! only to the company that he worked for 
@app.route("/create_new_flights", methods = ["GET", "POST"])
def staff_create_new_flights():
    if not check_staff_validity():
        flash ("Login Required")
        return redirect("/login")
    if not check_staff_role("admin"):
        flash ("admin required")
        return redirect("/home")
    airport_city = get_airport_city()
    airline_name = get_staff_airline()
    airplanes = get_airline_airplane(airline_name)
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call staff_view_flights_default(%s);", (airline_name, ))
    upcoming = cursor.fetchall()
    cursor.close()
    print(upcoming)
    if request.method == "GET":
        return render_template("staff_create_new_flights.html", airport_city = airport_city, airline_name = airline_name, upcoming = upcoming, airplanes = airplanes)  
    elif request.method == "POST":
        print("form data", request.form)
        # get all the needed data from html form 
        flight_num = request.form.get("flight_num")
        departure_time = request.form.get("departure_date") + " "+request.form.get("departure_time")
        arrival_time = request.form.get("arrival_date") + " "+request.form.get("arrival_time")
        price = request.form.get("price")
        status = request.form.get("status")
        airplane_id = request.form.get("airplane_id")
        arrive_airport = request.form.get("arrive")
        depart_airport = request.form.get("depart")
        # check if all the required fields are filled in
        if not (flight_num and departure_time and arrival_time and price and status and airplane_id and arrive_airport and depart_airport):
            flash("Input Incomplete")
            return redirect("/create_new_flights")
        # check if the flight already exists in the db!
        if check_duplicate_flight(airline_name, flight_num):
            flash("duplicate flight already existing!", "error")
            return redirect("/create_new_flights")
        # start writing to the table
        conn.reconnect()
        cursor = conn.cursor(prepared=True)
        cursor.execute("insert into flight values(%s, %s, %s, %s,%s, %s, %s, %s, %s );", (airline_name, flight_num, departure_time, arrival_time, price, status, airplane_id, arrive_airport, depart_airport))
        conn.commit()
        flash("Success Create New Flight")
        return redirect("/create_new_flights")
    
class NewAirportForm(FlaskForm):
    name = StringField("Airport Name (6 Characters MAX)", [DataRequired(), length(max=6)])
    city = StringField("CityName (20 Characters Max)", validators=[DataRequired(), length(max=20)])
    submit = SubmitField()
    
# check if there is duplicate airport in the system, 
# returns true if there is duplicate
def check_duplicate_airport(airport_name):
    conn.reconnect()
    cursor = conn.cursor(prepared=True)
    cursor.execute("call check_duplicate_airport(%s);", (airport_name, ))
    result = cursor.fetchall()
    cursor.close()
    if result:
        return True
    else:
        return False

@app.route("/add_new_airport", methods = ["GET", "POST"])
def add_new_airport():
    # check if the user is indeed staff AND admin
    if not check_staff_validity():
        flash ("Login Required")
        return redirect("/login")
    if not check_staff_role("admin"):
        flash ("admin required")
        return redirect("/home")
    airport_city = get_airport_city()
    form =NewAirportForm()
    if request.method == "GET":
        return render_template("add_new_airport.html", form = form, airport_city = airport_city)
    if request.method == "POST":
        if form.validate_on_submit():
            name = form.name.data
            city = form.city.data
            if check_duplicate_airport(name):
                flash("Airport Already Exists!")
                return redirect("/add_new_airport")
            conn.reconnect()
            cursor = conn.cursor(prepared=True)
            cursor.execute("insert into airport values (%s, %s);", (name, city))
            conn.commit()
            cursor.close()
            flash("Success Adding Planes")
            return redirect("/home")
        else:
            flash("Input Error, Check Your Form")
            return redirect("/add_new_airport")
        
        

@app.route('/logout')
def logout():
    session.pop('role')
    session.pop('email')
    return redirect('/login')

def findname():
    conn.reconnect()
    cursor = conn.cursor()
    name_query = "select name from customer where email = '{}';"
    cursor.execute(name_query.format(session['email']))
    name = cursor.fetchone()
    cursor.close()
    return name[0]

def get_airline_name(flight_num):
    conn.reconnect()
    cursor = conn.cursor()
    name_query = "select airline_name from flight where flight_num = '{}';"
    cursor.execute(name_query.format(flight_num))
    airline_name = cursor.fetchone()[0]
    return airline_name