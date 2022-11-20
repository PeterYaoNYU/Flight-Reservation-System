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


