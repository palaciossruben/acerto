-- GET HOUR counts
select date_part('hour', created_at - interval '5 hours') h, count(*)
from users
where id > 562 group by h order by h;

-- GET DAY counts
select date_part('dow', created_at - interval '5 hours') d, count(*)
from users
where id > 562 group by d order by d;



--------------------------------------------------------------------------

-- GET hour of day effectiveness
with visits_by as (
    select date_part('hour', created_at - interval '5 hours') h
           , count(distinct ip) c
    from visitors
    where created_at > '2017-06-28'::timestamp
    group by h
    order by h
),

conversions_by as (
    select date_part('hour', created_at - interval '5 hours') h
           , count(*) c
    from users
    where created_at > '2017-06-28'::timestamp
    group by h
    order by h
)

select visits_by.h
    , conversions_by.c conversions_count
    , visits_by.c visits_count
    , conversions_by.c::float / visits_by.c::float * 100 ratio
from visits_by
    inner join conversions_by on visits_by.h = conversions_by.h
order by visits_by.h;

-- SUMMARY BETTER FROM 10am to 7 pm. Much better at: 6pm, 10am, 11,am, 1pm, 3pm



--------------------------------------------------------------------------

-- GET dow effectiveness
with visits_by as (
    select date_part('dow', created_at - interval '5 hours') d
           , count(distinct ip) c
    from visitors
    where created_at > '2017-06-28'::timestamp
    group by d
    order by d
),

conversions_by as (
    select date_part('dow', created_at - interval '5 hours') d
           , count(*) c
    from users
    where created_at > '2017-06-28'::timestamp
    group by d
    order by d
)

select visits_by.d
    , conversions_by.c conversions_count
    , visits_by.c visits_count
    , conversions_by.c::float / visits_by.c::float * 100 ratio
from visits_by
    inner join conversions_by on visits_by.d = conversions_by.d
order by visits_by.d;

-- SUMMARY BETTER FROM Tuesday-Friday. Much better at: Thursday and friday



--------------------------------------------------------------------------

-- TODO: this would not work!!!
-- GET desktop vs mobile effectiveness
select



with visits_by as (
    select date_part('dow', created_at - interval '5 hours') d
           , count(distinct ip) c
    from visitors
    where created_at > '2017-06-28'::timestamp
    group by d
    order by d
),

conversions_by as (
    select date_part('dow', created_at - interval '5 hours') d
           , count(*) c
    from users
    where created_at > '2017-06-28'::timestamp
    group by d
    order by d
)

select visits_by.d
    , conversions_by.c conversions_count
    , visits_by.c visits_count
    , conversions_by.c::float / visits_by.c::float * 100 ratio
from visits_by
    inner join conversions_by on visits_by.d = conversions_by.d
order by visits_by.d;


