1.
# search city, get id
SELECT * FROM cities where name like '%Santiago de Cali%';

2.
# update with new alias
UPDATE cities SET alias='Cali' where id=75;

3.
# check update
SELECT * FROM cities where id=75;
