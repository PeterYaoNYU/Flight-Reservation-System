create table airline (
    airline_name    varchar(30),
    primary key (airline_name)
);

create table airplane(
    airline_name    varchar(30),
    id              VARCHAR(20),
    primary key (airline_name, id),
    foreign key (airline_name) references airline(airline_name)
        on delete cascade,
    index (id)
);

create table airport(
    name    varchar(6),
    city    varchar(20),
    primary key (name)
);

create table flight (
    airline_name    varchar(30),
    flight_num      varchar(20),
    departure_time  datetime,
    arrival_time    datetime,
    price           numeric(10,2),
    status          varchar(15),
    airplane_id     varchar(20),
    arrive_airport  varchar(6),
    depart_airport  varchar(6),
    primary key (airline_name, flight_num),
    foreign key (airline_name) references airline(airline_name)
        on delete cascade,
    foreign key (airplane_id) references airplane(id)
        on delete set null,
    foreign key (arrive_airport) references airport(name)
        on delete set null,
    foreign key (depart_airport) references airport(name)
        on delete set null,
    index (flight_num)
);

create table booking_agent(
    email               varchar(30),
    password            char(32),
    booking_agent_id    numeric(18, 0),
    primary key (email)
);

create table customer (
    email               varchar(30),
    name                varchar(20),
    password            char(32),
    building_number     numeric(5,0),
    street              varchar(20),
    city                varchar(20),
    state               varchar(15),
    phone_number        numeric(11),
    passport_number     varchar(15),
    passport_expiration date,
    passport_country    varchar(15),
    date_of_birth       date,
    primary key (email)
);

create table ticket (
    ticket_id           numeric(18),
    airline_name        varchar(30),
    flight_num          varchar(20),
    booking_agent_email varchar(30),
    customer_email      varchar(30),
    primary key (ticket_id),
    foreign key (airline_name) references airline(airline_name)
        on delete cascade,
    foreign key (flight_num) references flight(flight_num)
        on delete cascade,
    foreign key (booking_agent_email) references booking_agent(email)
        on delete set null,
    foreign key (customer_email) references customer(email)
        on delete set null
);

create table works_for (
    airline_name        varchar(30),
    booking_agent_email varchar(30),
    primary key (airline_name, booking_agent_email),
    foreign key (airline_name) references airline(airline_name)
        on delete cascade,
    foreign key (booking_agent_email) references booking_agent(email)
        on delete cascade
);

create table airline_staff (
    username        varchar(20),
    password        char(32),
    first_name      varchar(15),
    last_name       varchar(15),
    date_of_birth   date,
    airline_name    varchar(30),
    primary key (username),
    foreign key (airline_name) references airline(airline_name)
        on delete set null
);

create table permission (
    permit_to_do    varchar(10),
    primary key (permit_to_do)
);

create table staff_permission (
    username        varchar(20),
    permit_to_do    varchar(10),
    primary key (username, permit_to_do),
    foreign key (username) references airline_staff(username)
        on delete cascade,
    foreign key (permit_to_do) references permission(permit_to_do)
        on delete cascade
);