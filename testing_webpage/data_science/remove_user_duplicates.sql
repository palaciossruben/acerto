-- Removes users with repeating emails. Takes the last user.
with aggregate as (
    select email,
        max(id) max_id,
        count(*) user_count
    from users
    group by email
    order by user_count desc
),

duplicates as (
    select *
    from aggregate
    where user_count > 1
),

ids_to_delete as (select users.id
from users
where users.email in (select distinct email from duplicates)
 and users.id not in (select max_id from duplicates)
)

delete from users
where id in (select * from ids_to_delete);