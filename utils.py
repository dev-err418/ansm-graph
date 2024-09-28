import re
from datetime import datetime

def str_to_date(date_str):
    regexes = [
        re.compile(r'^(?P<day>[0-9]{2})/(?P<month>[0-9]{2})/(?P<year>[0-9]{4})$'),
        re.compile(r'^(?P<day>[0-9]{2})-(?P<month>[0-9]{2})-(?P<year>[0-9]{4})$'),
        re.compile(r'^(?P<year>[0-9]{4})-(?P<month>[0-9]{2})-(?P<day>[0-9]{2})$'),
    ]
    for regex in regexes:
        match = regex.match(date_str)
        if match:
            groups = match.groupdict()
            return datetime(int(groups['year']), int(groups['month']), int(groups['day'])).isoformat()
    raise ValueError(f'The format of this date is not accepted: "{date_str}".')

def date_to_str(date):
    def number_to_str(number, length=2):
        number = str(number)
        while len(number) < length:
            number = '0' + number
        return number

    day = number_to_str(date.day)
    month = number_to_str(date.month)
    year = number_to_str(date.year, 4)
    return f'{day}/{month}/{year}'

def remove_leading_zeros(string):
    if not string:
        return string
    replaced = re.sub(r'^[0]+', '', string)
    if not replaced:
        raise ValueError(f'Incorrect string: {string}')
    return replaced
