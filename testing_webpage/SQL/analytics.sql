-- GET HOURS
select date_part('hour', created_at - interval '5 hours') h, count(*) from users where id > 562 group by h order by h;

-- GET DAYS
select date_part('dow', created_at - interval '5 hours') d, count(*) from users where id > 562 group by d order by d;
