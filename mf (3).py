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
main_url = 'https://beta.serviceclarity.com/'
token = ''

# requests config
s = requests.Session()

# logging config
logging.basicConfig(filename='sc.log', level=logging.DEBUG)

# colorama config
init(autoreset=True)

# for schedule test
metric_fact = 100.0


# endregion

# region Access
def log_in(user, password):
    try:
        s.auth = (user, password)
        r = s.post(f'{main_url}pub/login/')
        log_status(r)

        global token
        token = r.json()['id']

        return r

    except requests.exceptions.RequestException as ex:
        logging.getLogger().debug(f'{type(ex)}: {ex.args}')


def log_out():
    try:
        h = {'Cookie': s.cookies.get('session'), 'Authorization': f'Bearer:{token}'}
        r = s.post(f'{main_url}api/logout/', headers=h)
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

    if breakdown is not None:
        payload['breakdown'] = breakdown

    try:
        r = s.post(f'{main_url}api/collector/', headers=h, json=payload)
        log_status(r)

        return r

    except requests.exceptions.RequestException as ex:
        logging.getLogger().debug(f'{type(ex)}: {ex.args}')


# endregion

# region Tools
def log_status(r):
    timestamp = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())
    if r.ok:
        logging.getLogger().debug(f'{timestamp} - OK')
    else:
        logging.getLogger().debug(f'{timestamp} - Error')


# endregion


def next_metric_fact(mf):
    # based on https://stackoverflow.com/a/8597889
    vol = 0.20
    change_percent = 2 * vol * rd.random()
    if change_percent > vol:
        change_percent -= (2 * vol)
    change_amount = mf * change_percent
    return mf + change_amount


def job(user, password, metric_id):
    global metric_fact
    metric_fact = next_metric_fact(metric_fact)

    log_in(user, password)
    r = upload_metric_data(metric_id, 0, metric_fact)

    if r.ok:
        print(f'{Back.GREEN}{r.status_code}{Back.RESET} - {r.request.body}')
    else:
        print(f'{Back.RED}{r.status_code}{Back.RESET} - {r.request.body}')
    log_out()


@begin.start(auto_convert=True)
def main(user, password, metric_id, minutes: 'Minutes between uploads'=60.0):
    print('started at: ' + Style.BRIGHT + '{:%Y%m%d%H%M}'.format(datetime.datetime.now()))
    print(f'User: {Fore.BLUE}{user}{Fore.RESET}. Every {Fore.BLUE}{minutes}{Fore.RESET} minute(s) upload fake'
          f' metric fact to metric id {Fore.BLUE}{metric_id}{Fore.RESET}.')

    schedule.every(minutes).minutes.do(job, user=user, password=password, metric_id=metric_id)

    while True:
        schedule.run_pending()
        time.sleep(1)
