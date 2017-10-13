import sys
sys.path.append("..")  # Adds higher directory to python modules path.

from testing_webpage.business import search_module


search_text = 'android'


users = search_module.get_matching_users2(search_text)

print(users)
