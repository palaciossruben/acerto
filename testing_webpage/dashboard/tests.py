from django.test import TestCase

import common


class MyClass:
    pass


class MyClass2:
    pass


assert 'type_id' == common.get_object_attribute_name('12_my_class_type_id', MyClass())

# recursive case
assert '13_my_class2_type_id' == common.get_object_attribute_name('12_my_class_13_my_class2_type_id', MyClass())
assert 'type_id' == common.get_object_attribute_name('13_my_class2_type_id',
                                                     MyClass2())

