"""
This a base file, that cannot import any models.
As it will refactor code among models. Its is used to solve the
circular dependency problem of having "common.py" import models and also refactor model code.
"""
import re


def change_to_international_phone_number(phone, calling_code, add_plus=False):

    plus_symbol = '+' if add_plus else ''

    if phone:
        phone = phone.replace('-', '')

        # Adds the '+' and country code
        if phone[0] != '+':
            phone = plus_symbol + calling_code + phone

            # Adds the '+' only
        elif re.search(r'^' + calling_code + '.+', phone) is not None:
            phone = plus_symbol + phone

    return phone
