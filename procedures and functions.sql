delimiter //
create procedure
    flight.purchase_ticket(in arrive_airport varchar(6), in depart_airport varchar(6), in departure_date date, out airline_name varchar(20), out flight_num varchar(20), out departure_time datetime, out arrival_time datetime, out price numeric(10, 2))
begin
    with avail_airplane_id as(
        select flight_num, airplane_id, seats
        from flight f join airplane a on(a.id = f.airplane_id)
        where f.depart_airport = depart_airport and f.arrive_airport=arrive_airport and date(departure_time) = departure_date
    ),
    seats_taken as(
        select flight_num, count(customer_email) as taken
        from ticket natural join avail_airplane_id
        group by flight_num
    )
    select airline_name, flight_num, departure_time, arrival_time, price
    from flight natural join avail_airplane_id natural join seats_taken
    where avail_airplane_id.seats - seats_taken.taken > 0;
end //

create function customer_purchase(arrive_airport varchar(6), depart_airport varchar(6), departure_date date)
    returns table(
        airline_name varchar(20),
        flight_num varchar(20),
        departure_time datetime,
        arrival_time datetime,
        price numeric(10, 2)
    )
    begin
        return table(
            with avail_airplane_id as(
                select flight_num, airplane_id, seats
                from flight f join airplane a on(a.id = f.airplane_id)
                where f.depart_airport = depart_airport and f.arrive_airport=arrive_airport and date(departure_time) = departure_date
            ),
            seats_taken as(
                select flight_num, count(customer_email) as taken
                from ticket natural join avail_airplane_id
                group by flight_num
            )
            select airline_name, flight_num, departure_time, arrival_time, price
            from flight natural join avail_airplane_id natural join seats_taken
            where avail_airplane_id.seats - seats_taken.taken > 0
    end
    );

with avail_airplane_id as(
    select flight_num, airplane_id, seats
    from flight f join airplane a on(a.id = f.airplane_id)
    where f.depart_airport = 'PVG' and f.arrive_airport='JFK' and date(departure_time) = '2022-11-01'
),
seats_taken as(
    select flight_num, count(customer_email) as taken
    from ticket natural join avail_airplane_id
    group by flight_num
)
select airline_name, flight_num, departure_time, arrival_time, price
from flight natural join avail_airplane_id natural join seats_taken
where avail_airplane_id.seats - seats_taken.taken > 0;


delimiter //
create procedure getCompany(
    in agentEmail varchar(30)
)
begin
    select airline_name from works_for where booking_agent_email = agentEmail;
end //
delimiter ;

delimiter //
create procedure getAirportCity()
begin
    select * from airport;
end //
delimiter ;

delimiter //
create procedure agentSearchNoDate(
    in depart varchar(30),
    in arrive varchar(30),
    in agentEmail varchar(30)
)
begin
    with avail_airlines as(
        select airline_name
        from works_for
        where booking_agent_email = agentEmail
    )
    select airline_name, flight_num, departure_time, arrival_time, price, status, airplane_id, concat(arrive_airport, '/', (select city from airport where name = arrive_airport)), concat(depart_airport, '/', (select city from airport where name = depart_airport))
    from flight as f
    where f.airline_name in (select * from avail_airlines)
    and f.departure_time > NOW()
    and f.arrive_airport = arrive
    and f.depart_airport = depart
    and (select count(*) from ticket t where t.flight_num = f.flight_num) < 
        (select seats from airplane a where a.id = f.airplane_id and a.airline_name = f.airline_name);
end//
delimiter ;

delimiter //
create procedure agentSearchWithDate(
    in depart varchar(30),
    in arrive varchar(30),
    in departDate varchar(30),
    in agentEmail varchar(30)
)
begin
    with avail_airlines as(
        select airline_name
        from works_for
        where booking_agent_email = agentEmail
    )
    select airline_name, flight_num, departure_time, arrival_time, price, status, airplane_id, concat(arrive_airport, '/', (select city from airport where name = arrive_airport)), concat(depart_airport, '/', (select city from airport where name = depart_airport))
    from flight as f
    where f.airline_name in (select * from avail_airlines)
    and DATE(f.departure_time) = departDate
    and f.arrive_airport = arrive
    and f.depart_airport = depart
    and (select count(*) from ticket t where t.flight_num = f.flight_num) < 
        (select seats from airplane a where a.id = f.airplane_id and a.airline_name = f.airline_name);
end//
delimiter ;

-- to provide safety check layer for agent_purchase_confirmation
delimiter //
create procedure agentPurchaseConfirm(
    in airlineName varchar(30),
    in flightNum varchar(30),
    in agentEmail   varchar(30)
)
begin
    declare seatsTaken int;
    declare totalSeats int;
    declare airplaneId int;

    SELECT airplane_id into airplaneId
    from flight
    where flight_num = flightNum and airline_name = airlineName;

    select seats
    into totalSeats
    from airplane
    WHERE id = airplaneId and airline_name = airlineName;

    SELECT count(*)
    into seatsTaken
    from ticket t
    where t.airline_name = airlineName
    and t.flight_num = flightNum;

    if totalSeats > seatsTaken and airlineName in (select airline_name from works_for where agentEmail = booking_agent_email) then
        select * from flight f1 where f1.airline_name = airlineName and f1.flight_num = flightNum;
    end if;
end//
delimiter ;

delimiter //
create procedure agentPurchase(
    in airlineName  varchar(30),
    in flightNum    varchar(30),
    in bookingAgentEmail    varchar(30),
    in customerEmail    varchar(30)
)
begin
    declare nextTicketId int;

    select max(ticket_id)+1
    into nextTicketId 
    from ticket;

    insert into ticket VALUES (nextTicketId, airlineName, flightNum, bookingAgentEmail, customerEmail);
end//
delimiter ;

delimiter //
create procedure viewMyCommissionNotDefault(
    in agentEmail   varchar(30),
    in startDate    date,
    in dateRange    int,
    out totalAmount numeric(12,2),
    out averageCommission   numeric(12,2),
    out totalTicket int
)
begin
    select sum(price) * 0.1
    into totalAmount
    from ticket natural join flight
    where booking_agent_email=agentEmail
    and datediff(startDate, date(departure_time)) BETWEEN 0 and dateRange;

    select count(ticket_id) into totalTicket
    from ticket natural join flight
    where booking_agent_email = agentEmail
    and datediff(startDate, date(departure_time)) BETWEEN 0 and dateRange;

    SELECT totalAmount/totalTicket into averageCommission;
end//
delimiter ; 

-- top 5 customers based on the number of tickets bought
delimiter //
create procedure top_five_ticket_count(
    in agentEmail   varchar(30)
)
begin
    select name, customer_email, count(ticket_id) as ticket_count
    from (ticket t natural join flight f) join customer c on t.customer_email = c.email
    where t.booking_agent_email = agentEmail and departure_time BETWEEN DATE_SUB(now(), INTERVAL 6 MONTH) and now()
    group by customer_email, c.name
    order by ticket_count DESC
    limit 5;
end //
delimiter ;

delimiter //
create procedure top_five_commission_last_year(
    agentEmail  varchar(30)
)
begin
    select name, customer_email, sum(f.price) * 0.1 as commission 
    from (ticket t natural join flight f) join customer c on t.customer_email = c.email
    where t.booking_agent_email = agentEmail and departure_time BETWEEN DATE_SUB(now(), INTERVAL 1 YEAR) and now()
    group by customer_email, c.name
    order by commission DESC
    limit 5;
end//
delimiter ;

delimiter //
create procedure staff_view_flights_default (
    in airlineName varchar(30)
)
begin
    select airline_name, flight_num, departure_time, arrival_time, price, status, airplane_id, concat(arrive_airport, '/', (select city from airport where name = arrive_airport)), concat(depart_airport, '/', (select city from airport where name = depart_airport))
    from flight
    where airline_name = airlineName and departure_time between now() and date_add(now(), interval 30 day);
end//
delimiter ;

delimiter //
create procedure staff_view_flights_date (
    in airlineName  varchar(30),
    in startDate    date,
    in endDate      date
)
begin
    select airline_name, flight_num, departure_time, arrival_time, price, status, airplane_id, concat(arrive_airport, '/', (select city from airport where name = arrive_airport)), concat(depart_airport, '/', (select city from airport where name = depart_airport))
    from flight
    where airline_name = airlineName and departure_time between startDate and endDate;
end//
delimiter ;

delimiter //
create procedure staff_view_flights_city (
    in airlineName  varchar(30),
    in sourceCity   varchar(30),
    in destinationCity  varchar(30)
)
begin
    select airline_name, flight_num, departure_time, arrival_time, price, status, airplane_id, concat(arrive_airport, '/', (select city from airport where name = arrive_airport)), concat(depart_airport, '/', (select city from airport where name = depart_airport))
    from flight
    where airline_name = airlineName and depart_airport = sourceCity and arrive_airport = destinationCity and departure_time > now();
end//
delimiter ;


delimiter //
create procedure staff_view_flights_date_city (
    in airlineName  varchar(30),
    in startDate    date,
    in endDate      date,
    in sourceCity   varchar(30),
    in destinationCity  varchar(30)
)
begin
    select airline_name, flight_num, departure_time, arrival_time, price, status, airplane_id, concat(arrive_airport, '/', (select city from airport where name = arrive_airport)), concat(depart_airport, '/', (select city from airport where name = depart_airport))
    from flight
    where airline_name = airlineName and depart_airport = sourceCity and arrive_airport = destinationCity and date(departure_time) between startDate and endDate;
end//
delimiter ;

delimiter //
create procedure insert_new_staff(
    in username    varchar(30), 
    in password     varchar(32),
    in first_name   varchar(15),
    in last_name    varchar(15),
    in date_of_birth    date,
    in airline_name varchar(30)
)
begin
    insert into airline_staff(username, password, first_name, last_name, date_of_birth, airline_name) values(username, md5(password), first_name, last_name, date_of_birth, airline_name);
end//
delimiter ;

delimiter //
create procedure check_duplicate(
    in role varchar(30),
    in pk   varchar(30)
)
begin
    if role = "airline_staff" then
        select * from airline_staff where username = pk;
    elseif role = "customer" then
        select * from customer where email = pk;
    else
        select * from booking_agent where email = pk;
    end if;
end//
delimiter ;


delimiter //
CREATE procedure check_staff_role(
    in user_name     varchar(30),
    in role         varchar(30)
)
begin
    select username
    from staff_permission
    where username = user_name and permit_to_do = role;
end //
delimiter ;


delimiter //
create procedure get_airline_airplane(
    in airline  varchar(30)
)
begin
    select id, seats
    from airplane
    where airline_name = airline;
end//
delimiter ;

delimiter //
create procedure check_duplicate_flight(
    in airlineName     varchar(30),
    in flightNum       varchar(30)
)
begin
    select *
    from flight
    where airline_name = airlineName and flight_num = flightNum;
end//
delimiter ;

delimiter //
create procedure update_flight_status(
    in airlineName     varchar(30),
    in flightNum       varchar(30),
    in new_status      varchar(30)
)
begin
    update flight
    set status = new_status
    where airline_name = airlineName and flight_num = flightNum;
end//
delimiter ;

delimiter //
create procedure check_duplicate_airport(
    in airport_name varchar(6)
)
begin
    select * from airport where name = airport_name;
end//
delimiter ;

delimiter //
create procedure check_duplicate_airplane(
    in airlineName  varchar(30),
    in planeId      int
)
begin
    select id from airplane where airline_name = airlineName and id = planeId;
end //
delimiter ;

delimiter //
create procedure staff_view_booking_agent(
    in airlineName  varchar(30),
    in benchmark    varchar(30),
    in dateRange    varchar(30)
)
begin
    if benchmark="ticket" and dateRange="year" then
        select booking_agent_email ,count(*) as total 
        from ticket natural join flight
        where booking_agent_email in (
            select w.booking_agent_email from works_for as w where w.airline_name = airlineName
        ) and (departure_time between DATE_SUB(NOW(), INTERVAL 1 YEAR) and NOW())
        group by booking_agent_email
        order by total desc
        limit 5;
    elseif benchmark = "ticket" and dateRange = "month" then
        select booking_agent_email, count(*) as total 
        from ticket natural join flight
        where booking_agent_email in (
            select w.booking_agent_email from works_for as w where w.airline_name = airlineName
        ) and (departure_time between DATE_SUB(NOW(), INTERVAL 1 MONTH) and NOW())
        group by booking_agent_email
        order by total desc 
        limit 5;
    elseif benchmark = "amount" and dateRange = "year" then
        select booking_agent_email ,sum(price) as total 
        from ticket natural join flight
        where booking_agent_email in (
            select w.booking_agent_email from works_for as w where w.airline_name = airlineName
        ) and (departure_time between DATE_SUB(NOW(), INTERVAL 1 YEAR) and now())
        group by booking_agent_email
        order by total desc
        limit 5;
    end if;
end //
delimiter ;

delimiter //
create procedure avail_booking_agent(
    in airlineName  varchar(30)
)
begin
    select b.email from booking_agent b where b.email not in (
        select booking_agent_email
        from works_for
        where airline_name = airlineName
    ) ;
end//
delimiter ;

delimiter //
create procedure top_destination_3_month(
    in airlineName  varchar(30)
)
begin
    with destination as (
        select count(ticket_id) as total, arrive_airport
        from ticket natural join flight
        where airline_name = airlineName and departure_time between DATE_SUB(date(now()), interval 3 MONTH) and now()
        group by arrive_airport
        order by total desc 
        limit 3
    )
    select concat(city, "/", arrive_airport), total
    from destination join airport on (destination.arrive_airport = airport.name);
end//
delimiter ;

delimiter //
create procedure top_destination_1_year(
    in airlineName  varchar(30)
)
begin
    with destination as (
        select count(ticket_id) as total, arrive_airport
        from ticket natural join flight
        where airline_name = airlineName and departure_time between DATE_SUB(date(now()), interval 1 YEAR) and now()
        group by arrive_airport
        order by total desc 
        limit 3
    )
    select concat(city, "/", arrive_airport), total
    from destination join airport on (destination.arrive_airport = airport.name);
end//
delimiter ;

delimiter //
create procedure frequent_customer(
    in airlineName  varchar(30)
)
begin
    select customer_email, count(ticket_id) as total
    from flight natural join ticket
    where airline_name = airlineName
    and departure_time between DATE_SUB(now(), INTERVAL 1 year) and now()
    group by customer_email
    order by total desc;
end//
delimiter ;

delimiter //
create procedure  all_flights_taken(
    in customerEmail    varchar(30),
    in airlineName      varchar(30)
)
begin
    select flight_num, date(departure_time), date(arrival_time), price, concat(arrive_airport, "/", (select city from airport where name = arrive_airport)), concat(depart_airport, "/", (select city from airport where name = depart_airport))
    from ticket natural join flight
    where customer_email = customerEmail and airline_name = airlineName
    order by departure_time desc;
end//
delimiter ;

delimiter //
create procedure get_all_staff(
    in airlineName  varchar(30)
)
begin 
    select username, first_name, last_name
    from airline_staff
    where airline_name = airlineName;
end//
delimiter ;

delimiter //
create procedure get_all_permission()
begin
    select * from permission;
end //
delimiter ;

delimiter //
create procedure grant_new_permission(
    in userName varchar(30),
    in newPermission   varchar(30)
)
begin
    insert ignore into staff_permission values (userName, newPermission);
end //
delimiter ;

delimiter //
create procedure comparisonRevenueEarned(
    in airlineName  varchar(30),
    out directSalesMonth    float,
    out directSalesYear     float,
    out totalSalesMonth     float,
    out totalSalesYear      float
)
begin
    select sum(price) into totalSalesMonth
    from flight natural JOIN ticket
    where airline_name = airlineName and departure_time BETWEEN DATE_SUB(NOW(), interval 1 month) and now();

    select sum(price) into totalSalesYear
    from flight natural JOIN ticket
    where airline_name = airlineName and departure_time BETWEEN DATE_SUB(NOW(), interval 1 YEAR) and now();

    select sum(price) into directSalesMonth
    from flight natural JOIN ticket
    where airline_name = airlineName and departure_time BETWEEN DATE_SUB(NOW(), interval 1 month) and now() and booking_agent_email is NULL;

    select sum(price) into directSalesYear
    from flight natural JOIN ticket
    where airline_name = airlineName and departure_time BETWEEN DATE_SUB(NOW(), interval 1 year) and now() and booking_agent_email is NULL;
end//
delimiter ;

delimiter //
create procedure view_reports(
    in airlineName  varchar(30),
    in beginDate    date,
    in endDate      date
)
begin
    select count(ticket_id) as total, year(departure_time) as year, month(departure_time) as month
    from ticket natural join flight
    where airline_name = airlineName and date(departure_time) between beginDate and endDate
    group by year(departure_time), month(departure_time);
end //
delimiter ;


    
