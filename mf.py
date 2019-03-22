import datetime
import time
import random as rd

import begin
import logging
import requests
import schedule
from colorama import init, Fore, Back, Style

# region Configs

# Service Clarity config
host = 'https://beta.serviceclarity.com/'
token = ''

# requests config
s = requests.Session()

# logging config
logging.basicConfig(filename='metricfaker.log', level=logging.DEBUG)
logging.getLogger('schedule').setLevel(logging.WARNING)  # to avoid showing username and password in log

# colorama config
init(autoreset=True)

# starting value
metric_fact = 100.0


# endregion

# region Access
def log_in(user, password):
    try:
        s.auth = (user, password)
        r = s.post(f'{host}pub/login/')
        log_status(r)

        global token
        token = r.json()['id']

        return r

    except requests.exceptions.RequestException as ex:
        logging.getLogger().debug(f'{type(ex)}: {ex.args}')


def log_out():
    try:
        h = {'Cookie': s.cookies.get('session'), 'Authorization': f'Bearer:{token}'}
        r = s.post(f'{host}api/logout/', headers=h)
        log_status(r)

        return r

    except requests.exceptions.RequestException as ex:
        logging.getLogger().debug(f'{type(ex)}: {ex.args}')


# endregion

# region Metrics
def upload_metric_data(metric, timestamp, fact, breakdown=None):
    # Upload data for pre-configured metric

    if timestamp <= 0:
        timestamp = '{:%Y%m%d%H%M}'.format(datetime.datetime.now())

    h = {
        'Cookie': s.cookies.get('session'),
        'Authorization': f'Bearer:{token}',
        'Content-Type': 'application/json',
    }

    payload = {
        'metric': str(metric),
        'time': int(timestamp),
        'fact': round(float(fact), 2),
    }

    # optional breakdown.
    if breakdown is not None:
        payload['breakdown'] = breakdown

    try:
        r = s.post(f'{host}api/collector/', headers=h, json=payload)
        log_status(r)

        return r

    except requests.exceptions.RequestException as ex:
        logging.getLogger().debug(f'{type(ex)}: {ex.args}')


# endregion

# region Tools
def log_status(r):
    if r.ok:
        logging.getLogger().debug(f'{get_timestamp()} - OK')
    else:
        logging.getLogger().debug(f'{get_timestamp()} - Error')


def get_timestamp():
    return '{:%Y%m%d%H%M}'.format(datetime.datetime.now())


# endregion

def job(user, password, metric_id):
    def next_metric_fact(last_value):
        vol = 0.05
        change_percent = 2 * vol * rd.random()
        if change_percent > vol:
            change_percent -= (2 * vol)
        change_amount = last_value * change_percent
        return last_value + change_amount

    global metric_fact
    metric_fact = next_metric_fact(metric_fact)

    log_in(user, password)

    r = upload_metric_data(metric_id, 0, metric_fact)

    if r.ok:
        print(f'{Back.GREEN}{r.status_code}{Back.RESET} - {r.request.body}')
    else:
        print(f'{Back.RED}{r.status_code}{Back.RESET} - {r.request.body}')

    log_out()


# begins module handles console args. "if __name__" not necessary.
@begin.start(auto_convert=True)
def main(user, password, metric_id, minutes: 'Minutes between uploads'=60, start: 'Initial value'=100):
    global metric_fact
    metric_fact = start

    logging.getLogger().info(f'Started at: {get_timestamp()}')
    print('started at: ' + Style.BRIGHT + get_timestamp())
    print(f'User: {Fore.BLUE}{user}{Fore.RESET}. Every {Fore.BLUE}{minutes}{Fore.RESET} minute(s) upload fake'
          f' metric fact to metric id {Fore.BLUE}{metric_id}{Fore.RESET}.')

    schedule.every(minutes).minutes.do(job, user=user, password=password, metric_id=metric_id)

    while True:
        schedule.run_pending()
        time.sleep(1)  # to avoid cpu drain
