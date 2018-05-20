select a.name, user_id
from surveys
left join answers a on a.id = answer_id
where test_id=4 and question_id=11;