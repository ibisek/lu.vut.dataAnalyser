
--DROP TABLE IF EXISTS configuration;
CREATE TABLE configuration (
	k VARCHAR(32) PRIMARY KEY NOT NULL, 
	v VARCHAR(128) NOT NULL
) charset utf8;
  

INSERT INTO configuration (k, v) VALUES ('FILE_INGESTION_ROOT', '/var/www/radec/ingestion');
INSERT INTO configuration (k, v) VALUES ('FILE_STORAGE_ROOT', '/var/www/radec/storage');


--DROP TABLE IF EXISTS equipment_types;
CREATE TABLE IF NOT EXISTS equipment_types (
  id INT PRIMARY KEY auto_increment,
  part_no VARCHAR(32) NOT NULL,
  label VARCHAR(32) NULL,
  description VARCHAR(64) NULL
) charset utf8;

INSERT INTO equipment_types (part_no, label) VALUES ('PI-1234', 'Pilatus PC-12');
INSERT INTO equipment_types (part_no, label) VALUES ('PW-1234', 'Pratt & Whitney Canada PT6 E');
INSERT INTO equipment_types (part_no, label) VALUES ('CE-1234', 'Cessna 172 Skyhawk');
INSERT INTO equipment_types (part_no, label) VALUES ('TP-1234', 'PBS TP100');

select * from equipment_types;


--DROP TABLE IF EXISTS components;
CREATE TABLE IF NOT EXISTS components (
  id INT PRIMARY KEY auto_increment,
  engine_id INT NULL REFERENCES engines.id,
  equipment_type_id INT NOT NULL REFERENCES equipment_types.id,
  serial_no VARCHAR(32) NULL
) charset utf8;

INSERT INTO components (engine_id, equipment_type_id, serial_no) VALUES (2, 6, 'sn_1234');
INSERT INTO components (engine_id, equipment_type_id, serial_no) VALUES (2, 8, 'sn_1234');
INSERT INTO components (engine_id, equipment_type_id, serial_no) VALUES (2, 9, 'sn_1234');
INSERT INTO components (engine_id, equipment_type_id, serial_no) VALUES (2, 10, 'sn_1234');

select * from components;



DROP TABLE IF EXISTS equipment_properties;
CREATE TABLE IF NOT EXISTS equipment_properties (
  id INT PRIMARY KEY auto_increment,
  equipment_type_id INT NOT NULL REFERENCES equipment_types.id,
  k VARCHAR(16) NOT NULL,
  v VARCHAR(32) NOT NULL
) charset utf8;

INSERT INTO equipment_properties (equipment_type_id, k, v) VALUES (10, 'ELC_LIMIT', '10450');

select * from equipment_properties;
select * from equipment_types;


--DROP TABLE IF EXISTS fleets;
CREATE TABLE IF NOT EXISTS fleets (
  id INT PRIMARY KEY auto_increment,
  label VARCHAR(32) NOT NULL,
  organisation_id INT NOT NULL REFERENCES organisations.id
) charset utf8;

INSERT INTO fleets (label, organisation_id) VALUES 
	('LU Virtual Fleet', 1);

select * from fleets;


--DROP TABLE IF EXISTS airplanes;
CREATE TABLE IF NOT EXISTS airplanes (
  id INT PRIMARY KEY auto_increment,
  equipment_id INT NOT NULL references equipment_types.id,
  model VARCHAR(32) NULL,
  year_of_prod INT(4) NULL,
  serial_no VARCHAR(32) NOT NULL,
  num_engines TINYINT(2) NOT NULL,
  registration VARCHAR(8) NOT NULL,
  num_landings INT NOT NULL DEFAULT 0,
  fleet_id INT NULL
) charset utf8;

INSERT INTO airplanes (equipment_id, model, year_of_prod, serial_no, num_engines, registration, num_landings, fleet_id) 
	VALUES (3, '172N', 2020, '2020_01', 1, 'OK-PBS', 0, 1);

INSERT INTO airplanes (equipment_id, model, year_of_prod, serial_no, num_engines, registration, num_landings, fleet_id) 
	VALUES (1, 'PC-12/47E', 2019, '2019_01', 1, 'OK-ABC', 0, 1);

select * from airplanes;


--DROP TABLE IF EXISTS engines;
CREATE TABLE IF NOT EXISTS engines (
  id INT PRIMARY KEY auto_increment,
  equipment_type_id INT NOT NULL references equipment_types.id,
  serial_no VARCHAR(32) NOT NULL,
  year_of_prod INT(4) NULL,
  airplane_id INT REFERENCES aircrafts.id,
  cycles INT NOT NULL DEFAULT 0,
  hours INT NOT NULL DEFAULT 0
) charset utf8;

INSERT INTO engines (equipment_type_id, serial_no, year_of_prod, cycles, hours) 
	VALUES (2, 'SN_2020_09', 2020, 0, 0);

INSERT INTO engines (equipment_type_id, serial_no, year_of_prod, cycles, hours) 
	VALUES (4, 'SN_2020_01', 2020, 0, 0);

select * from engines;

--DROP TABLE IF EXISTS airplane_engine;
CREATE TABLE IF NOT EXISTS airplane_engine (
  airplane_id INT NOT NULL references airplanes.id,
  engine_id INT NOT NULL references engines.id
) charset utf8;

INSERT INTO airplane_engine (airplane_id, engine_id) VALUES (1, 1);


--DROP TABLE IF EXISTS flights;
CREATE TABLE IF NOT EXISTS flights (
  id INT PRIMARY KEY auto_increment,
  airplane_id INT NOT NULL references airplanes.id,
  takeoff_ts INT NOT NULL,
  takeoff_lat DECIMAL(8,5) NULL,
  takeoff_lon DECIMAL(8,5) NULL,
  takeoff_location VARCHAR(4) NULL,
  landing_ts INT NULL,
  landing_lat DECIMAL(8,5) NULL,
  landing_lon DECIMAL(8,5) NULL,
  landing_location VARCHAR(4) NULL,
  duration INT NOT NULL DEFAULT 0,
  cycles_full INT NOT NULL DEFAULT 0,
  cycles_short INT NOT NULL DEFAULT 0
) charset utf8;


--DROP TABLE IF EXISTS flight_engine;
CREATE TABLE IF NOT EXISTS flight_engine (
  flight_id INT NOT NULL references fligts.id,
  engine_id INT NOT NULL references engines.id
) charset utf8;

--DROP TABLE IF EXISTS files;
CREATE TABLE IF NOT EXISTS files (
  id INT PRIMARY KEY auto_increment,
  name VARCHAR(32) NOT NULL,
  flight_id INT NULL,
  engine_id INT NOT NULL references engines.id,
  source BOOL NOT NULL DEFAULT 0,
  generated BOOL NOT NULL DEFAULT 0,
  status INT NOT NULL DEFAULT 0,
  hash VARCHAR(256) NULL
) charset utf8;


--DROP TABLE IF EXISTS regression_results;
CREATE TABLE IF NOT EXISTS regression_results (
  id INT PRIMARY KEY auto_increment,
  ts INT DEFAULT 0, 
  engine_id INT REFERENCES engines.id, 
  file_id INT REFERENCES files.id, 
  function VARCHAR(16) NOT NULL, 
  x_value FLOAT(20) DEFAULT 0, 
  y_value FLOAT(20) DEFAULT 0, 
  delta FLOAT(20) DEFAULT 0, 
  a FLOAT(20) DEFAULT 0, 
  b FLOAT(20) DEFAULT 0, 
  c FLOAT(20) DEFAULT 0, 
  x_min FLOAT(20) DEFAULT 0, 
  x_max FLOAT(20) DEFAULT 0
) charset utf8;


--DROP TABLE IF EXISTS organisations;
CREATE TABLE IF NOT EXISTS organisations (
  id INT PRIMARY KEY auto_increment,
  name VARCHAR(64) NOT NULL,
  vat VARCHAR(16) NULL,
  address VARCHAR(255) NULL,
  super TINYINT(1) NOT NULL,
  enabled TINYINT(1) NOT NULL
) charset utf8;

INSERT INTO organisations (name, vat, address, super, enabled) VALUES 
	('LU.VUT', 'CZ00216305', 'Letecký ústav, Technická 2896/2, 616 69 Brno, CZ', true, true);
select * from organisations;


--DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY auto_increment,
  login VARCHAR(32) NOT NULL,
  password VARCHAR(256) NOT NULL,
  salt VARCHAR(255) BINARY NOT NULL,
  name VARCHAR(32) NOT NULL,
  surname VARCHAR(32) NOT NULL,
  email VARCHAR(128) NOT NULL,
  enabled TINYINT(1) NULL,
  admin TINYINT(1) NOT NULL DEFAULT 0,
  organisation_id INT NOT NULL REFERENCES organisations.id
) charset utf8;

--


select * from configuration;

--delete from files;
insert into files (name, engine_id, source, status) values ('testing1.csv', 1, true, 1);

update files set status = 1 where id = 672;
select * from files;

--delete from files;

SELECT count(*) FROM files WHERE source = true AND status=1;

select * from files where status = 1;
select * from files where status > 10;
update files set status = 1 where status = 2;
update files set status = 1 where id=681;

select count(*) from regression_results;
select * from regression_results;


--delete from regression_results where file_id is not null;

select function, value, a, b, c, x_min, x_max from regression_results where engine_id = 1 AND file_id IS NULL;


select * from regression_results;
select distinct(function) from regression_results where engine_id=1;
select * from regression_results where ts != 0 and file_id is not null and engine_id=1 order by ts asc;

select * from regression_results where ts = 0 and file_id is null and engine_id=1;

select * from configuration;