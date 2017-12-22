


select *
from questions_answers
inner join questions_answers qa on qa.question_id =



-- Deprecated users.campaign no longer in use. Instead use candidate.campaign
select e.*, ue.*, u.name from evaluations e
inner join users_evaluations ue on ue.evaluation_id = e.id
inner join users u on u.id = ue.user_id
where u.campaign_id in (11, 12, 13);

