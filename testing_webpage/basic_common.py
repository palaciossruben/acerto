"""
This a base file, that cannot import any models.
As it will refactor code among models. Its is used to solve the
circular dependency problem of having "common.py" import models and also refactor model code.
"""
import re
ADMIN_USER_EMAIL = 'admin@peaku.co'


def change_to_international_phone_number(phone, calling_code, add_plus=False):

    plus_symbol = '+' if add_plus else ''

    if phone:
        phone = phone.replace('-', '')

        # Adds the '+' only
        if re.search(r'^' + calling_code + '.+', phone) is not None:
            phone = plus_symbol + phone
        elif phone[0] != '+':  # Adds the '+' and country code phone

            # TODO: change for other countries
            max_phone_length = 10
            if len(phone) > max_phone_length:
                phone = ''.join(phone[-10:-1])
            phone = plus_symbol + calling_code + phone

    return phone


def not_admin_user(request):
    return request.user.username != ADMIN_USER_EMAIL


def is_admin(user):
    username = user.get_username()
    return user.get_username() == ADMIN_USER_EMAIL