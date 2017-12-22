import unicodedata


# TODO: duplicate code: see subscribe.helper
def remove_accents_in_string(element):
    """
    Args:
        element: anything.
    Returns: Cleans accents only for strings.
    """
    if isinstance(element, str):
        return ''.join(c for c in unicodedata.normalize('NFD', element) if unicodedata.category(c) != 'Mn')
    else:
        return element


# TODO: duplicate code: see subscribe.helper
def remove_accents(an_object):
    """
    Several different objects can be cleaned.
    Args:
        an_object: can be list, string, tuple and dict
    Returns: the cleaned obj, or a exception if not implemented.
    """
    if isinstance(an_object, str):
        return remove_accents_in_string(an_object)
    elif isinstance(an_object, list):
        return [remove_accents_in_string(e) for e in an_object]
    elif isinstance(an_object, tuple):
        return tuple([remove_accents_in_string(e) for e in an_object])
    elif isinstance(an_object, dict):
        return {remove_accents_in_string(k): remove_accents_in_string(v) for k, v in an_object.items()}
    else:
        raise NotImplementedError


def translate_users(users, language_code):
    """
    Args:
        users: List of Users
        language_code: can be 'es'
    Returns: List of translated users
    """
    if 'es' in language_code:
        for u in users:
            if u.profession is not None:
                u.profession.name = u.profession.name_es

            if u.education is not None:
                u.education.name = u.education.name_es
