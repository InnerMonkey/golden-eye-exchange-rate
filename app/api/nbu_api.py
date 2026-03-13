import xml.etree.ElementTree as ET

import requests

from api import _Api

class Api(_Api):
    def __init__(self):
        super().__init__("NBU_Api")

    def _update_rate(self, xrate):
        rate = self._get_nbu_rate(xrate.from_currency)
        return rate

    def _get_nbu_rate(self, from_currency):
        response = self._send_request(url="https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?xml", method="get")
        self.log.debug("response.encoding: %s", response.encoding)
        response_text = response.text
        self.log.debug("response.text: %s", response_text)
        rate = self._find_rate(response_text, from_currency)

        return rate

    def _find_rate(self, response_text, from_currency):
        root = ET.fromstring(response_text)
        values = root.findall("currency")

        nbu_valute_map = {978: "EUR"}
        currency_nbu_alias = nbu_valute_map[from_currency]

        for value in values:
            if value.find("cc").text == currency_nbu_alias:
                return float(value.find("rate").text)
        raise ValueError("Invalid NBU response: %s not found", from_currency)
