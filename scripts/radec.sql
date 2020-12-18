
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
  num_landings INT NOT NULL DEFAULT 0
) charset utf8;

INSERT INTO airplanes (equipment_id, model, year_of_prod, serial_no, num_engines, registration, registration_country) 
	VALUES (1, 'PC-12/47E', 2019, '2019_01', 1, 'OK-ABC', 'cz');

INSERT INTO airplanes (equipment_id, model, year_of_prod, serial_no, num_engines, registration, registration_country) 
	VALUES (2, '172N', 2020, '2020_01', 1, 'OK-PBS', 'cz');

INSERT INTO airplanes (equipment_id, model, year_of_prod, serial_no, num_engines, registration, registration_country) 
	VALUES (3, 'NG', 2020, '2020_11', 1, 'OK-GEAC', 'cz');

select * from airplanes;


--DROP TABLE IF EXISTS engines;
CREATE TABLE IF NOT EXISTS engines (
  id INT PRIMARY KEY auto_increment,
  equipment_id INT NOT NULL references equipment.id,
  serial_no VARCHAR(32) NOT NULL,
  year_of_prod INT(4) NULL,
  airplane_id INT REFERENCES aircrafts.id,
  engine_no INT default 0, -- alocation on the airframe
  flight_id INT REFERENCES flights.id,
  archived BOOL default false,
  status VARCHAR(16),
  -- eng.counters:
  cycle_hours INT default 0,
  takeoff_hours INT default 0,
  CYCLENo INT default 0,
  CYCLENoTO FLOAT default 0,
  CYCLERep FLOAT default 0,
  EqCyle FLOAT default 0,
  EqCycleSim FLOAT default 0,
  EngNumNPExcA int default 0,
  EngNumNPExcB int default 0
  EngITTExcA INT default 0,
  EngITTExcB INT default 0,
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


--DROP TABLE IF EXISTS airplanes_organisations;
CREATE TABLE IF NOT EXISTS airplanes_organisations (
  airplane_id INT NOT NULL references airplanes.id,
  organisation_id INT NOT NULL references organisations.id,
  relation_type VARCHAR(1) NOT NULL DEFAULT 'O'
) charset utf8;

INSERT INTO airplanes_organisations (airplane_id, organisation_id, relation_type) VALUES (1, 1, 'O');	-- LU.VUT - PC12
INSERT INTO airplanes_organisations (airplane_id, organisation_id, relation_type) VALUES (2, 1, 'O');	-- LU.VUT - C172
INSERT INTO airplanes_organisations (airplane_id, organisation_id, relation_type) VALUES (3, 2, 'O');	-- LU.VUT - L410NG


--DROP TABLE IF EXISTS airplanes_engines;
CREATE TABLE IF NOT EXISTS airplanes_engines (
  airplane_id INT NOT NULL references airplanes.id,
  engine_id INT NOT NULL references engines.id
) charset utf8;

INSERT INTO airplanes_engines (airplane_id, engine_id) VALUES (1, 1);


--DROP TABLE IF EXISTS flights;
CREATE TABLE IF NOT EXISTS flights (
  id INT PRIMARY KEY auto_increment,
  root_id INT DEFAULT NULL references flights.id,
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
  LNDHeavy FLOAT default false,
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


--DROP TABLE IF EXISTS engines_flights;
CREATE TABLE IF NOT EXISTS engines_flights (
  engine_id INT NOT NULL references engines.id,
  flight_id INT NOT NULL references fligts.id
) charset utf8;

--DROP TABLE IF EXISTS file_formats;
CREATE TABLE IF NOT EXISTS file_formats (
  id INT PRIMARY KEY auto_increment,
  name VARCHAR(32) NOT NULL
) charset utf8;

INSERT INTO file_formats (name) VALUES ('PT6');
INSERT INTO file_formats (name) VALUES ('H80AI');
INSERT INTO file_formats (name) VALUES ('H80GE');

--DROP TABLE IF EXISTS files;
CREATE TABLE IF NOT EXISTS files (
  id INT PRIMARY KEY auto_increment,
  name VARCHAR(32) NOT NULL,
  raw BOOL DEFAULT false,
  format INT NOT NULL references file_formats.id,
  status INT NOT NULL DEFAULT 0,
  hash VARCHAR(256) NULL
) charset utf8;

alter table files add column format INT NOT NULL references file_formats.id;

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

--DROP TABLE IF EXISTS files_flights;
CREATE TABLE IF NOT EXISTS files_flights (
  file_id INT references files.id,
  flight_id INT references flights.id
) charset utf8;

--DROP TABLE IF EXISTS cycles;	
CREATE TABLE IF NOT EXISTS cycles (
  id INT PRIMARY KEY auto_increment,
  root_id INT DEFAULT NULL references cycles.id,
  idx INT NOT NULL DEFAULT 0,
  engine_id INT NOT NULL references engines.id,
  flight_id INT NOT NULL references flights.id,
  file_id INT references files.id,
  type VARCHAR(1),
  -- equivalent cycles flags:
  NoSU INT DEFAULT 0,
  TOflag INT DEFAULT 0,
  RTOflag INT DEFAULT 0,
  -- over limit flags:
  NGlimL BOOL,
  NPlimL BOOL,
  ITTlimL BOOL,
  ITTOpMax FLOAT,
  ITTSUmax FLOAT,
  ITTSUgrad FLOAT,
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
  NGTO FLOAT,
  NPTO FLOAT,
  TQTO FLOAT,
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

--DROP TABLE IF EXISTS notifications;
CREATE TABLE IF NOT EXISTS notifications (
  id INT PRIMARY KEY auto_increment,
  type INT NOT NULL,
  airplane_id INT references airplanes.id,
  engine_id INT references engines.id,
  cycle_id INT references cycles.id,
  flight_id INT references flights.id,
  message VARCHAR(255) NOT NULL,
  checked bool DEFAULT false
) charset utf8;

select * from notifications;

--DROP TABLE IF EXISTS logbook;
CREATE TABLE IF NOT EXISTS logbook (
  id INT PRIMARY KEY auto_increment,
  ts INT NOT NULL,
  engine_id INT references engines.id,
  airplane_id INT references cycles.id,
  component_id INT references components.id,
  entry VARCHAR(255) NOT NULL
) charset utf8;

select * from logbook;

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

select count(*) from regression_results;
select * from regression_results;


--delete from regression_results where file_id is not null;

select function, value, a, b, c, x_min, x_max from regression_results where engine_id = 1 AND file_id IS NULL;


select * from regression_results;
select distinct(function) from regression_results where engine_id=1;
select * from regression_results where ts != 0 and file_id is not null and engine_id=1 order by ts asc;

select * from regression_results where ts = 0 and file_id is null and engine_id=1;

select * from configuration;

--
--insert into files (name, raw, hash) values ('log_190323_090817_LKTB.csv', true, '0c4db7ec609361af08af2829713292b3e502ae79060e7861ad4d9b27573d2791');
--insert into files (name, raw, hash) values ('Engine data FDR-3.txt', true, '19a0fccce9673bf34e58b097f3d06de1466ebc8f829d9d2f83e823c345172b8b');
select * from files;
--insert into flights_files (flight_id, file_id) values (1, 1);
--insert into flights_files (flight_id, file_id) values (2, 2);
select * from flights_files;

--insert into engines_flights values(1,1);	-- PT6
--insert into engines_flights values(2,2);	-- H80.1
--insert into engines_flights values(3,2);	-- H80.2
--select * from engines_flights;

select * from flights;

select * from airplanes;

select * from engines;

select * from equipment;

select * from files;

select * from cycles;

select * from notifications order by id desc;

select * from logbook order by id desc;

--delete from cycles where id=1;
--insert into cycles (id, engine_id, flight_id, file_id) values(20,1,1,1);
--insert into cycles (id, engine_id, flight_id, file_id) values(21,2,2,2);
--insert into cycles (id, engine_id, flight_id, file_id) values(22,3,2,2);

--delete from flights where root_id=2;
--delete from cycles where root_id=22;

