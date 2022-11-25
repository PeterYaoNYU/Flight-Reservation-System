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
        (select seats from airplane a where a.id = f.airplane_id);
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
        (select seats from airplane a where a.id = f.airplane_id);
end//
delimiter ;

-- to provide safety check layer for agent_purchase_confirmation
delimiter //
create procedure agentPurchaseConfirm(
    in airlineName varchar(30),
    in flightNum varchar(30)
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
    WHERE id = airplaneId;

    SELECT count(*)
    into seatsTaken
    from ticket t
    where t.airline_name = airlineName
    and t.flight_num = flightNum;

    if totalSeats > seatsTaken then
        select * from flight f1 where f1.airline_name = airlineName and f1.flight_num = flightNum;
    end if;
end//
delimiter ;



