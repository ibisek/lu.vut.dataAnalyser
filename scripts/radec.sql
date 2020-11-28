
--DROP TABLE IF EXISTS configuration;
CREATE TABLE configuration (
	k VARCHAR(32) PRIMARY KEY NOT NULL, 
	v VARCHAR(128) NOT NULL
) charset utf8;
  

INSERT INTO configuration (k, v) VALUES ('FILE_INGESTION_ROOT', '/var/www/radec/ingestion');
INSERT INTO configuration (k, v) VALUES ('FILE_STORAGE_ROOT', '/var/www/radec/storage');


DROP TABLE IF EXISTS equipment;
CREATE TABLE IF NOT EXISTS equipment (
  id INT PRIMARY KEY auto_increment,
  type VARCHAR(1),
  part_no VARCHAR(32) NOT NULL,
  label VARCHAR(32) NULL,
  description VARCHAR(64) NULL
) charset utf8;

INSERT INTO equipment (type,part_no, label) VALUES ('A', 'PI-1234', 'Pilatus PC-12');
INSERT INTO equipment (type,part_no, label) VALUES ('A','CE-1234', 'Cessna 172 Skyhawk');
INSERT INTO equipment (type,part_no, label) VALUES ('A','AI-1234', 'L-410 UVP-E20');
INSERT INTO equipment (type,part_no, label) VALUES ('E','PW-1234', 'Pratt & Whitney Canada PT6 E');
INSERT INTO equipment (type,part_no, label) VALUES ('E','TP-1234', 'PBS TP100');
INSERT INTO equipment (type,part_no, label) VALUES ('E','GE-1234', 'GE H80');
INSERT INTO equipment (type,part_no,label,description) VALUES ('C','M601-6081.2','Propeller Shaft',null);
INSERT INTO equipment (type,part_no,label,description) VALUES ('C','M601-6081.5','Propeller Shaft',null);
INSERT INTO equipment (type,part_no,label,description) VALUES ('C','M601-4004.5','Free Turbine Shaft',null);
INSERT INTO equipment (type,part_no,label,description) VALUES ('C','M601-4004.7','Free Turbine Shaft',null);
INSERT INTO equipment (type,part_no,label,description) VALUES ('C','M601-3220.5','Free Turbine Disc',null);
INSERT INTO equipment (type,part_no,label,description) VALUES ('C','M601-3156.5','Rear Shaft',null);
INSERT INTO equipment (type,part_no,label,description) VALUES ('C','M601-3156.9','Rear Shaft',null);

select * from equipment;


--DROP TABLE IF EXISTS components;
CREATE TABLE IF NOT EXISTS components (
  id INT PRIMARY KEY auto_increment,
  engine_id INT NULL REFERENCES engines.id,
  equipment_id INT NOT NULL REFERENCES equipment.id,
  serial_no VARCHAR(32) NULL,
  archived BOOL
) charset utf8;

INSERT INTO components (engine_id, equipment_id, serial_no, archived) VALUES (2, 6, 'sn_1234', false);
INSERT INTO components (engine_id, equipment_id, serial_no, archived) VALUES (2, 8, 'sn_1234', false);
INSERT INTO components (engine_id, equipment_id, serial_no, archived) VALUES (2, 9, 'sn_1234', false);
INSERT INTO components (engine_id, equipment_id, serial_no, archived) VALUES (2, 10, 'sn_1234', false);

select * from components;


--DROP TABLE IF EXISTS equipment_properties;
CREATE TABLE IF NOT EXISTS equipment_properties (
  id INT PRIMARY KEY auto_increment,
  equipment_type_id INT NOT NULL REFERENCES equipment.id,
  k VARCHAR(16) NOT NULL,
  v VARCHAR(32) NOT NULL,
  units VARCHAR(8)
) charset utf8;

--INSERT INTO equipment_properties (equipment_type_id, k, v) VALUES (10, 'ELC_LIMIT', '10450');

select * from equipment_properties;
select * from equipment;


--DROP TABLE IF EXISTS fleets;
CREATE TABLE IF NOT EXISTS fleets (
  id INT PRIMARY KEY auto_increment,
  owner_org_id INT NOT NULL REFERENCES organisations.id,
  label VARCHAR(32) NOT NULL
) charset utf8;

INSERT INTO fleets (owner_org_id, label) VALUES (1, 'LU Virtual Fleet');
INSERT INTO fleets (owner_org_id, label) VALUES (2, 'GEAC Virtual Fleet');

select * from fleets;


--DROP TABLE IF EXISTS airplanes;
CREATE TABLE IF NOT EXISTS airplanes (
  id INT PRIMARY KEY auto_increment,
  equipment_id INT NOT NULL references equipment.id,
  model VARCHAR(32) NULL,
  year_of_prod INT(4) NULL,
  serial_no VARCHAR(32) NOT NULL,
  num_engines TINYINT(2) NOT NULL,
  registration VARCHAR(8) NOT NULL,
  registration_country VARCHAR(2) NOT NULL,
  num_landings INT NOT NULL DEFAULT 0,
  fleet_id INT NULL
) charset utf8;

INSERT INTO airplanes (equipment_id, model, year_of_prod, serial_no, num_engines, registration, registration_country, fleet_id) 
	VALUES (1, 'PC-12/47E', 2019, '2019_01', 1, 'OK-ABC', 'cz', 1);

INSERT INTO airplanes (equipment_id, model, year_of_prod, serial_no, num_engines, registration, registration_country, fleet_id) 
	VALUES (2, '172N', 2020, '2020_01', 1, 'OK-PBS', 'cz', 1);

INSERT INTO airplanes (equipment_id, model, year_of_prod, serial_no, num_engines, registration, registration_country, fleet_id) 
	VALUES (3, 'NG', 2020, '2020_11', 1, 'OK-GEAC', 'cz', 2);

select * from airplanes;


--DROP TABLE IF EXISTS engines;
CREATE TABLE IF NOT EXISTS engines (
  id INT PRIMARY KEY auto_increment,
  equipment_id INT NOT NULL references equipment.id,
  serial_no VARCHAR(32) NOT NULL,
  year_of_prod INT(4) NULL,
  airplane_id INT REFERENCES aircrafts.id,
  engine_no INT default 0, -- alocation on the airframe
  archived BOOL default false,
  status VARCHAR(16),
  -- eng.counters:
  CYCLENo INT default 0,
  CYCLENoTO FLOAT default 0,
  CYCLERep FLOAT default 0,
  EqCyle FLOAT default 0,
  EqCycleSim FLOAT default 0,
  -- components:
  ACD1NoC FLOAT default 0,
  ACD1NoCS FLOAT default 0,
  ACD1NoR FLOAT default 0,
  ACD2NoC FLOAT default 0,
  ACD2NoCS FLOAT default 0,
  ACD2NoR FLOAT default 0,
  ImpNoC FLOAT default 0,
  ImpNoCS FLOAT default 0,
  ImpNoR FLOAT default 0,
  MShaftNoC FLOAT default 0,
  MShaftNoCS FLOAT default 0,
  MShaftNoR FLOAT default 0,
  FRSNoC FLOAT default 0,
  FRSNoCS FLOAT default 0,
  FRSNoR FLOAT default 0,
  CTDNoC FLOAT default 0,
  CTDNoCS FLOAT default 0,
  CTDNoR FLOAT default 0,
  RShaftNoC FLOAT default 0,
  RShaftNoCS FLOAT default 0,
  RShaftNoR FLOAT default 0,
  FTDNoC FLOAT default 0,
  FTDNoCS FLOAT default 0,
  FTDNoR FLOAT default 0,
  FShaftNoC FLOAT default 0,
  FShaftNoCS FLOAT default 0,
  FShaftNoR FLOAT default 0,
  PShaftNo FLOAT default 0,
  PShaftNoR FLOAT default 0
) charset utf8;

INSERT INTO engines (equipment_id, serial_no, year_of_prod, engine_no, airplane_id, archived, status) 
	VALUES (4, 'SN_2020_01', 2020, 1, 1, false, 'ok');	-- PT6 @ PC-12

INSERT INTO engines (equipment_id, serial_no, year_of_prod, engine_no, airplane_id, archived, status) 
	VALUES (6, 'SN_2020_02', 2020, 1, 3, false, 'ok'); -- H80 @ NG

INSERT INTO engines (equipment_id, serial_no, year_of_prod, engine_no, airplane_id, archived, status) 
	VALUES (6, 'SN_2020_03', 2020, 2, 3, false, 'ok'); -- H80 @ NG

select * from engines;


--DROP TABLE IF EXISTS airplanes_engines;
CREATE TABLE IF NOT EXISTS airplanes_engines (
  airplane_id INT NOT NULL references airplanes.id,
  engine_id INT NOT NULL references engines.id
) charset utf8;

INSERT INTO airplanes_engines (airplane_id, engine_id) VALUES (1, 1);


--DROP TABLE IF EXISTS flights;
CREATE TABLE IF NOT EXISTS flights (
  id INT PRIMARY KEY auto_increment,
  idx INT DEFAULT 0,
  airplane_id INT NOT NULL references airplanes.id,
  takeoff_ts INT NULL,
  takeoff_lat DECIMAL(8,5) NULL,
  takeoff_lon DECIMAL(8,5) NULL,
  takeoff_location VARCHAR(4) NULL,
  landing_ts INT NULL,
  landing_lat DECIMAL(8,5) NULL,
  landing_lon DECIMAL(8,5) NULL,
  landing_location VARCHAR(4) NULL,
  flight_time INT NOT NULL DEFAULT 0,
  operation_time INT NOT NULL DEFAULT 0,
  LNDCount INT default 0,
  LNDHeavy FLOAT,
  NoSUL INT default 0,
  NoSUR INT default 0,
  NoTOAll INT default 0,
  NoTORep INT default 0,
  ABC BOOL default false,
  AFOn BOOL default false,
  APOn BOOL default false,
  VetAcc BOOL default false,
  AuxPumpOn BOOL default false,
  PitchLock BOOL default false
) charset utf8;

INSERT INTO flights (airplane_id) VALUES (1);
INSERT INTO flights (airplane_id) VALUES (3);

select * from flights;


--DROP TABLE IF EXISTS flights_engines;
CREATE TABLE IF NOT EXISTS flights_engines (
  flight_id INT NOT NULL references fligts.id,
  engine_id INT NOT NULL references engines.id
) charset utf8;

--DROP TABLE IF EXISTS files;
CREATE TABLE IF NOT EXISTS files (
  id INT PRIMARY KEY auto_increment,
  name VARCHAR(32) NOT NULL,
  raw BOOL DEFAULT false,
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

--DROP TABLE IF EXISTS flights_files;
CREATE TABLE IF NOT EXISTS flights_files (
  flight_id INT references flights.id,
  file_id INT references files.id
) charset utf8;

--DROP TABLE IF EXISTS organisations;
CREATE TABLE IF NOT EXISTS organisations (
  id INT PRIMARY KEY auto_increment,
  name VARCHAR(64) NOT NULL,
  vat VARCHAR(16) NULL,
  address VARCHAR(255) NULL,
  super TINYINT(1) NOT NULL,
  enabled TINYINT(1) NOT NULL,
  url VARCHAR(255)
) charset utf8;

alter table organisations ADD COLUMN url VARCHAR(255);

INSERT INTO organisations (name, vat, address, super, enabled) VALUES 
	('LU.VUT', 'CZ00216305', 'Letecký ústav, Technická 2896/2, 616 69 Brno, CZ', true, true, 'https://lu.fme.vutbr.cz/');
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


--DROP TABLE IF EXISTS cycles;
CREATE TABLE IF NOT EXISTS cycles (
  id INT PRIMARY KEY auto_increment,
  engine_id INT NOT NULL references engines.id,
  flight_id INT NOT NULL references flights.id,
  file_id INT references files.id,
  type VARCHAR(1),
  -- over limit flags:
  NGlimL BOOL,
  NPlimL BOOL,
  ITTlimL BOOL,
  TQlimL BOOL,
  OilPlimL BOOL,
  FuelPlimL BOOL,
  FireWarning BOOL,
  -- engine start-up mode:
  BeTimeSU INT,
  TimeSUg INT,
  TimeSUgIdle INT,
  TimePeHeat INT,
  ITTSUg FLOAT,
  ALTSUg FLOAT,
  OilP FLOAT,
  OilTBe FLOAT,
  FuelP FLOAT,
  CASmax FLOAT,
  EndTimeSU INT,
  -- take-off mode:
  BeTimeTO INT,
  TimeTO INT,
  NGRTO FLOAT,
  NPTO FLOAT,
  TQ FLOAT,
  ITTTO FLOAT,
  AltTO FLOAT,
  OilPMinTO FLOAT,
  OilPMaxTO FLOAT,
  OilTMaxTO FLOAT,
  FuelPMinTO FLOAT,
  FuelPMaxTO FLOAT,
  EndTimeTO INT,
  -- climb mode
  BeTimeClim INT,
  TimeClim INT,
  NGRClim FLOAT,
  NPClim FLOAT,
  TQClim FLOAT,
  ITTClim FLOAT,
  ALTClim FLOAT,
  OilPMinClim FLOAT,
  OilPMaxClim FLOAT,
  OilTMaxClim FLOAT,
  FuelPMinClim FLOAT,
  FuelPMaxClim FLOAT,
  EndTimeClim INT,
  -- cruise mode:
  BeTimeCruis INT,
  NGCruis FLOAT,
  NPCruis FLOAT,
  TQCruis FLOAT,
  ITTCruis FLOAT,
  AltCruis FLOAT,
  OilPMinCruis FLOAT,
  OilPMaxCruis FLOAT,
  OilTMaxCruis FLOAT,
  FuelPMinCruis FLOAT,
  FuelPMaxCruis FLOAT,
  EndTimeCruis INT,
  -- idle mode:
  BeTimeIdle INT,
  TimeIdle INT,
  TimeIdleHyPumpIdle INT,
  NGIdle FLOAT,
  ITTIdle FLOAT,
  AltIdle FLOAT,
  OilPMinIdle FLOAT,
  OilPMaxIdle FLOAT,
  OilTMaxIdle FLOAT,
  FuelPMinIdle FLOAT,
  FuelPMaxIdle FLOAT,
  EndTimeIdle INT
) charset utf8;

select * from cycles;

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

select id, login, admin from users;

--
--insert into files (name, raw, hash) values ('log_190323_090817_LKTB.csv', true, '0c4db7ec609361af08af2829713292b3e502ae79060e7861ad4d9b27573d2791');
select * from files;
--insert into flights_files (flight_id, file_id) values (1, 1);
select * from flights_files;
--insert into flights_engines values(1,1);
select * from flights_engines;

select * from flights;

select * from airplanes;

select * from engines;

select * from files;

select * from cycles;

delete from cycles;
