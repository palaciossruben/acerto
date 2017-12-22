"""
All Campaign editing related stuff on the dashboard, except for candidates and interviews.
"""
import re
from django.shortcuts import redirect

from beta_invite.models import Bullet, Campaign


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


def create_campaign(request):
    """
    saves to create id first.
    """

    campaign = Campaign()
    campaign.save()

    update_campaign_basic_properties(campaign, request)
    update_campaign_bullets(campaign, request)

    return campaign
