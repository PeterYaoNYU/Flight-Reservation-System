-- a
insert into airline values ('China Eastern');

-- b
insert into airport values ('JFK', 'NYC');
insert into airport values ('PVG', 'Shanghai');

-- c
insert into customer values ('taylorswift@gmail.com', 'Taylor Swift', md5('20021228'), 1555, 'Century Ave', 'Shanghai', 'Shanghai', 18019271972, 'G1111', '2025.10.10', 'USA', '1989.12.13');
insert into customer values ('realdonaldtrump@gamil.com', 'Donald Trump', md5('maga'), 1600, 'Pennsylvania Ave', 'Washington D.C', 'Washington D.C', 911, 'G2222', '2022.10.1', 'USA', '1946.6.14');
insert into booking_agent values ('bookingagent1@gmail.com', md5(20021228), 0001);

-- d
insert into airplane values ('China Eastern', 00001);
insert into airplane values ('China Eastern', 00002);
insert into airplane values ('China Eastern', 985);
insert into airplane values ('China Eastern', 211);

-- e
insert into airline_staff values ('China Eastern CEO', md5('20021228'), 'Yuncheng', 'Yao', '2002.12.28', 'China Eastern');

-- f
insert into flight values ('China Eastern', 'MU001', '2022.11.1 6:00:00', '2022-11-1 20:00:00', 20000, 'upcoming', 1, 'JFK', 'PVG');
insert into flight values ('China Eastern', 'MU002', '2022.10.17 12:00:00', '2022-10-18 2:00:00', 30000, 'in_progress', 2, 'JFK', 'PVG');
insert into flight values ('China Eastern', 'MU003', '2022.10.16 6:00:00', '2022-10-16 20:00:00', 10000, 'delayed', 1, 'PVG', 'JFK');
insert into flight values ('China Eastern', 'MU004', '2022.12.1 6:00:00', '2022-12-1 20:00:00', 70000, 'upcoming', 2, 'JFK', 'PVG');

-- g
insert into ticket values (1111, 'China Eastern', 'MU001', NULL, 'taylorswift@gmail.com');
insert into ticket values (2222, 'China Eastern', 'MU002', 'bookingagent1@gmail.com', 'realdonaldtrump@gamil.com');
insert into ticket values (3333, 'China Eastern', 'MU003', 'bookingagent1@gmail.com', 'realdonaldtrump@gamil.com');
