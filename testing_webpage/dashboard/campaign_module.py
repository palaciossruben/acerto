"""
All Campaign editing related stuff on the dashboard, except for candidates and interviews.
"""
import re
from django.shortcuts import redirect

import common
from beta_invite.models import Bullet, Campaign, City, Test, Question, QuestionType, Answer
from business import prospect_module


def update_bullet_attr(campaign, dict_id, key_bullet_dict, value, attribute_name):
    """
    Uses meta-programing, and updates or creates new Bullet objects.
    Args:
        campaign: Object
        dict_id: temporal id to distinguish between different new ids only.
        key_bullet_dict: dictionary containing new stored bullets to add.
        value:
        attribute_name: the name of the Bullet object attribute.
    Returns: None, just update
    """
    if dict_id in key_bullet_dict.keys():  # Updates bullet.
        b = key_bullet_dict[dict_id]
        setattr(b, attribute_name, value)
        b.save()
    else:  # creates new Bullet
        b = Bullet(**{attribute_name: value})
        b.save()
        if b.name_es != "":
            key_bullet_dict[dict_id] = b
            campaign.bullets.add(b)


def update_campaign_basic_properties(campaign, request):
    """
    Bit of meta-programming to update properties assuming a perfect match between model properties and names in the HTML
    Args:
        campaign: Campaign Object
        request: HTTP request
    Returns: None, just updates the campaign object.
    """
    for key, value in request.POST.items():
        if hasattr(Campaign, key):
            setattr(campaign, key, value)

    campaign.save()


def get_campaign_edit_url(campaign):
    return redirect('/dashboard/campaign/edit/{}'.format(campaign.id))


def get_bullets_url(campaign):
    return redirect('/dashboard/campaign/{}/bullets'.format(campaign.id))


def update_campaign_bullets(campaign, request):
    """
    Args:
        campaign: Campaign Object
        request: HTTP request
    Returns: None, updates or creates new bullets.
    """
    key_bullet_dict = {}
    for key, value in request.POST.items():

        # When there is a new_bullet.
        if 'new_bullet' in key:

            dict_id = int(re.findall('^\d+', key)[0])

            if 'type' in key:
                update_bullet_attr(campaign, dict_id, key_bullet_dict, value, 'bullet_type_id')

            elif re.match(r'.*bullet_name$', key):
                update_bullet_attr(campaign, dict_id, key_bullet_dict, value, 'name')

            elif re.match(r'.*bullet_name_es$', key):
                update_bullet_attr(campaign, dict_id, key_bullet_dict, value, 'name_es')

        # updates existing bullets
        elif re.search('\d+_bullet', key):

            # gets the bullet id.
            bullet_pk = int(re.findall(r'\d+', key)[0])
            bullet = Bullet.objects.get(pk=bullet_pk)

            if 'type' in key:
                bullet.bullet_type_id = value

            elif re.match(r'.*bullet_name$', key):
                bullet.name = value

            elif re.match(r'.*bullet_name_es$', key):
                bullet.name_es = value

            bullet.save()

    campaign.save()


def add_user_tests(campaign, request):
    """
    Adds tests that are not yet on the campaign
    :param campaign:
    :param request:
    :return:
    """
    tests_ids = {int(id) for id in request.POST.getlist('test_ids')}.difference({t.id for t in campaign.tests.all()})
    campaign.tests.add(*tests_ids)
    campaign.save()


def create_campaign(request):
    """
    saves to create id first.
    """

    country = common.get_country_with_request(request)

    city_id = request.POST.get('city_id')
    if city_id:
        city = City.objects.get(pk=city_id)
    else:
        city = common.get_city(request)

    campaign = Campaign(country=country, city=city)
    campaign.save()

    update_campaign_basic_properties(campaign, request)
    update_campaign_bullets(campaign, request)

    candidate_prospects = prospect_module.get_candidates(campaign)
    prospect_module.send_mails(candidate_prospects)

    add_default_tests(campaign)
    add_user_tests(campaign, request)

    return campaign


def get_city_question(campaign):
    q = Question(text='Are you willing to move to {} for this job?'.format(campaign.city.name),
                 text_es='¿Estarías dispuesto/a a mudarte a {} por este trabajo?'.format(campaign.city.name),
                 type=QuestionType.objects.get(code='SA'))
    q.save()

    yes = Answer(name='Yes', name_es='Si', order=1)
    yes.save()
    no = Answer(name='No', name_es='No', order=2)
    no.save()

    q.answers = [yes, no]
    q.correct_answers = [yes]
    q.save()

    return q


def get_salary_question(campaign):
    q = Question(text='What is your salary expectation?',
                 text_es='¿Cúal es tu salario esperado?',
                 type=QuestionType.objects.get(code='NI'))
    q.params = {'min': 0,
                'max': 30_000_000,
                'min_correct': campaign.salary_low_range,
                'max_correct': campaign.salary_high_range,
                'default': 1_000_000
                }

    q.save()

    return q


def get_experience_question(campaign):

    q = Question(text='How many years of experience do you have?',
                 text_es='¿Cuantos años de experiencia tienes?',
                 type=QuestionType.objects.get(code='NI'))
    q.params = {'min': 0, 'max': 100, 'min_correct': campaign.experience, 'max_correct': 100, 'default': 1}
    q.save()

    return q


def get_requirements_test(campaign):
    """
    Simple test, asking for city,
    :param campaign:
    :return:
    """
    q1 = get_city_question(campaign)
    q2 = get_salary_question(campaign)
    q3 = get_experience_question(campaign)

    test = Test(name='Requirements: {}'.format(campaign.title_es),
                name_es='Requisitos: {}'.format(campaign.title_es),)
    test.save()
    test.questions = [q1, q2, q3]
    test.save()

    return test


def add_default_tests(campaign):
    cognitive_test = Test.objects.get(name='Cognitive Test')
    requirement_test = get_requirements_test(campaign)

    campaign.tests = [cognitive_test, requirement_test]
    campaign.save()
