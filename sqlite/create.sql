create table hk (id integer primary key, detector integer, hk_date date, hk_time integer, processed_time datetime);  
create table startup (id integer primary key, detector integer, name char(64), processed_time datetime);  
create table status (id integer primary key, run integer, detector integer, filename integer, bytes integer, processed_time datetime) ;
create table header (id integer primary key, run integer, detector integer, filename integer, bytes integer, processed_time datetime) ;
create table event  (id integer primary key, run integer, detector integer, filename integer, bytes integer, processed_time datetime) ;

