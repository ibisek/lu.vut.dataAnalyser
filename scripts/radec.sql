
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
  label VARCHAR(32) NULL
) charset utf8;

INSERT INTO equipment_types (label) VALUES ('Pilatus PC-12');
INSERT INTO equipment_types (label) VALUES ('Pratt & Whitney Canada PT6 E');


--DROP TABLE IF EXISTS airplanes;
CREATE TABLE IF NOT EXISTS airplanes (
  id INT PRIMARY KEY auto_increment,
  type_id INT NOT NULL references equipment_types.id,
  model VARCHAR(32) NULL,
  year_of_prod INT(4) NULL,
  serial_no VARCHAR(32) NOT NULL,
  num_engines TINYINT(1) NOT NULL,
  registration VARCHAR(8) NOT NULL,
  num_landings INT NOT NULL DEFAULT 0,
  fleet_id INT NULL
) charset utf8;

INSERT INTO radec.airplanes (type_id, model, year_of_prod, serial_no, num_engines, registration, num_landings, fleet_id) 
	VALUES (1, 'NGX', 2020, '2020_01', 1, 'OK-NGX', 0, NULL);


--DROP TABLE IF EXISTS engines;
CREATE TABLE IF NOT EXISTS engines (
  id INT PRIMARY KEY auto_increment,
  type_id INT NOT NULL references equipment_types.id,
  serial_no VARCHAR(32) NOT NULL,
  year_of_prod INT(4) NULL,
  cycles INT NOT NULL DEFAULT 0,
  hours INT NOT NULL DEFAULT 0
) charset utf8;

INSERT INTO engines (type_id, serial_no, year_of_prod, cycles, hours) 
	VALUES (2, '2020_02', 2020, 0, 0);


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
  value FLOAT(20) DEFAULT 0, 
  a FLOAT(20) DEFAULT 0, 
  b FLOAT(20) DEFAULT 0, 
  c FLOAT(20) DEFAULT 0, 
  x_min FLOAT(20) DEFAULT 0, 
  x_max FLOAT(20) DEFAULT 0
) charset utf8;


--


select * from configuration;

--delete from files;
insert into files (name, engine_id, source, status) values ('testing1.csv', 1, true, 1);

update files set status = 1 where id = 1;
select * from files;

select * from files where status=1;

select * from regression_results;

--delete from regression_results;


