import requests
import logging
from models import XRate, peewee_datetime
from config import LOGGER_CONFIG
import xml.etree.cElementTree as ET

log = logging.getLogger("NBUApi")
fh = logging.FileHandler(LOGGER_CONFIG["file"])
fh.setLevel(LOGGER_CONFIG["level"])
fh.setFormatter(LOGGER_CONFIG["formatter"])
log.addHandler(fh)
log.setLevel(LOGGER_CONFIG["level"])

def update_xrates(from_currency, to_currency):
    log.info("Started update for: %s => %s", from_currency, to_currency)
    xrate = XRate.select().where(XRate.from_currency == from_currency,
                                 XRate.to_currency == to_currency).first()
    
    log.debug("rate before: %s", xrate)
    xrate.rate = get_nbu_rate(from_currency)
    xrate.updated = peewee_datetime.datetime.now()
    xrate.save()

    log.debug("rate after: %s", xrate)
    log.info("Finished update for: %s => %s", from_currency, to_currency)

def get_nbu_rate(from_currency):
    response = requests.get("https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?xml")
    log.debug("response.encoding: %s", response.encoding)
    response_text = response.text
    log.debug("response.text: %s", response_text)
    eur_rate = find_eur_rate(response_text)

    return eur_rate

def find_eur_rate(response_text):
    root = ET.fromstring(response_text)
    values = root.findall("currency")
    for value in values:
        if value.find("cc").text == "EUR":
            return float(value.find("rate").text)
    raise ValueError("Invalid NBU response: USD not found")
