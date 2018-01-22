create table hk (id integer primary key, detector integer, hk_date date, hk_time integer, processed_time datetime);  
create index hk_index on hk(hk_date,hk_time); 
create table startup (id integer primary key, detector integer, name char(64), processed_time datetime);  
create table status (id integer primary key, run integer, detector integer, filename integer, bytes integer, processed_time datetime) ;
create index status_index on status(filename); 
create table header (id integer primary key, run integer, detector integer, filename integer, bytes integer, processed_time datetime) ;
create index header_index on header(filename); 
create table event  (id integer primary key, run integer, detector integer, filename integer, bytes integer, processed_time datetime) ;
create index event_index on event(filename); 

