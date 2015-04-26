create schema if not exists autopresentr;
use autopresentr;

drop table if exists logs;

create table logs (
  id int(11) primary key not null auto_increment,
  user_ip varchar(255),
  user_agent varchar(255),
  subject varchar(255),
  is_random boolean default 0,
  created_at timestamp default current_timestamp
) engine=innodb charset=utf8;
