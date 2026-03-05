import requests

from models import XRate, peewee_datetime

import logging
from config import LOGGER_CONFIG

log = logging.getLogger("PrivatBankApi")
fh = logging.FileHandler(LOGGER_CONFIG["file"])
fh.setLevel(LOGGER_CONFIG["level"])
fh.setFormatter(LOGGER_CONFIG["formatter"])
log.addHandler(fh)
log.setLevel(LOGGER_CONFIG["level"])

def update_xrates(from_currency, to_currency):
    log.info("Started update for: %s -> %s", from_currency, to_currency)
    #Отримання курсу із БД
    xrate = XRate.select().where(XRate.from_currency == from_currency,
                                 XRate.to_currency == to_currency).first()
    
    log.debug("rate before: %s", xrate)
    #отримання нового значення курсу від Приват банку і збереження в об"єкт xrate
    xrate.rate = get_privat_rate(from_currency)
    #оновлення поля updated
    xrate.updated = peewee_datetime.datetime.now()
    xrate.save()
    log.debug("rate after: %s", xrate)
    log.info("Finished update for: %s -> %s", from_currency, to_currency)


def get_privat_rate(from_currency):
    response = requests.get("https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
    response_json = response.json()
    log.debug("Privat response: %s", response_json)
    usd_rate = find_usd_rate(response_json)

    return usd_rate

def find_usd_rate(response_data):
    for el in response_data:
        if el["ccy"] == "USD":
            return float(el["sale"])
    
    raise ValueError("Invalid Privat response: USD not found")


