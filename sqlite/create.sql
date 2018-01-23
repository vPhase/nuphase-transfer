create table hk (id integer primary key autoincrement , detector integer, hk_date date, hk_time integer, processed_time datetime default(datetime('now')), north_file_id integer, south_file_id, integer);  
create index hk_index on hk(hk_date,hk_time); 

create table startup (id integer primary key autoincrement, detector integer, name text, processed_time datetime default(datetime('now')), north_file_id integer, south_file_id, integer );  

create table status (id integer primary key autoincrement, run integer, detector integer, filename integer, bytes integer, processed_time datetime default(datetime('now')), north_file_id integer, south_file_id, integer) ;
create index status_index on status(filename); 

create table header (id integer primary key autoincrement, run integer, detector integer, filename integer, bytes integer, processed_time datetime default(datetime('now')), north_file_id integer, south_file_id, integer) ;
create index header_index on header(filename); 

create table event  (id integer primary key autoincrement, run integer, detector integer, filename integer, bytes integer, processed_time datetime default(datetime('now')), north_file_id integer, south_file_id, integer) ;
create index event_index on event(filename); 

create table north_tar_files (id integer primary key autoincrement, tar_file text, procesed_time datetime default(datetime('now')) ); 
create table south_tar_files (id integer primary key autoincrement, tar_file text, procesed_time datetime default(datetime('now')) ); 

