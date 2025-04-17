import requests
from datetime import datetime
from datetime import date
import pygal

def convert_date(str_date):
    return datetime.strptime(str_date, '%Y-%m-%d').date()