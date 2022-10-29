create database user_details
use user_details 
create table team
(
userID int primary key,
username varchar(50),
password varchar(50),
email varchar(50),
rollno int
)
insert into details values (1,'Mohanraj','Mohanraj123','Mohanraj@gmail.com',211419205106);
insert into details values (2,'Jagadesh','Jagadesh123','Jagadesh@gmail.com',211419205072);
insert into details values (3,'Ganesh','Ganesh123','Ganesh@gmail.com',211419205050);
insert into details values (4,'Ahileshwaran','Ahileshwaran123','Ahileshwaran@gmail.com',211419205010);
select*from team
delete from team where userID=4
update team set username='justin' where userID=4