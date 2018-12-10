import pdfkit
from testing_webpage import settings

base_url = 'http://127.0.0.1:8000' if settings.DEBUG else 'https://peaku.co'
pdfkit.from_url(base_url + '/cv', 'cv.pdf')
