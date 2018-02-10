create table status_summary(id integer primary key autoincrement, unixtime float,  rate float, avg_rate float, max_rate float, min_rate float); 
create table hk_summary(id integer primary key autoincrement, unixtime float,  temp_master integer, temp_slave integer, temp_case integer, current_master integer, current_slave integer, current_frontend integer); 

create index status_summary_index on status_summary(unixtime); 
create index hk_summary_index on hk_summary(unixtime); 



