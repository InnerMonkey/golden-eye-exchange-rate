import unittest
import requests
import json
from unittest.mock import patch

import api.test_api as test_api
import models
import api.privatbank_api as privatbank_api
import api.nbu_api as nbu_api
import api

def get_privat_response(*args, **kwargs):
    print("get_privat_response")

    class Response:
        def __init__(self, response):
            self.text = json.dumps(response)
        def json(self):
            return json.loads(self.text)
    return Response([{"ccy": "USD", "base_ccy": "UAH", "buy": "43.90000", "sale": "44.44444"}])

class Test(unittest.TestCase):
    def setUp(self):
        models.init_db()

    def test_main(self):
        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 20)
        test_api.update_xrates(840, 980)
        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated

        self.assertEqual(xrate.rate, 20.01)
        self.assertGreater(updated_after, updated_before)

    def test_privat_currency_error(self):
        xrate = models.XRate.get(id=1)
        self.assertEqual(xrate.rate, 20)

        self.assertRaises(ValueError, privatbank_api.Api().update_rate, 978, 980)

    def test_privat_usd(self):

        xrate = models.XRate.get(id = 1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 20)

        privatbank_api.Api().update_rate(840, 980)

        xrate = models.XRate.get(id = 1)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 25)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
        self.assertIsNotNone(api_log.response_text)

        self.assertIn('{"ccy":"USD","base_ccy":"UAH",', api_log.response_text)

    def test_privat_btc(self):

        xrate = models.XRate.get(from_currency=1000, to_currency=840)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 1.0)

        privatbank_api.Api().update_rate(1000, 840)

        xrate = models.XRate.get(from_currency=1000, to_currency=840)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 5000)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
        
    def test_nbu(self):
        xrate = models.XRate.get(from_currency = 978, to_currency = 980)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 45)

        nbu_api.Api().update_rate(978, 980)

        xrate = models.XRate.get(from_currency = 978, to_currency = 980)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 50)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange?xml")
        self.assertIsNotNone(api_log.response_text)

        self.assertIn('<r030>978</r030>', api_log.response_text)

    @patch("api._Api._send", new=get_privat_response)
    def test_privat_mock(self):
        
        xrate = models.XRate.get(id = 1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 20)

        privatbank_api.Api().update_rate(840, 980)

        xrate = models.XRate.get(id = 1)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 25)
        self.assertGreater(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
        self.assertIsNotNone(api_log.response_text)

        self.assertIn('[{"ccy": "USD", "base_ccy": "UAH", "buy": "43.90000", "sale": "44.44444"}]', api_log.response_text)

    def test_api_error(self):
        api.HTTP_TIMEOUT = 0.001
        xrate = models.XRate.get(id=1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 20)

        self.assertRaises(requests.exceptions.RequestException, privatbank_api.Api().update_rate, 840, 980)

        xrate = models.XRate.get(id=1)
        updated_after = xrate.updated

        self.assertEqual(xrate.rate, 20)
        self.assertEqual(updated_after, updated_before)

        api_log = models.ApiLog.select().order_by(models.ApiLog.created.desc()).first()

        self.assertIsNotNone(api_log)
        self.assertEqual(api_log.request_url, "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
        self.assertIsNone(api_log.response_text)
        self.assertIsNotNone(api_log.error)

        error_log = models.ErrorLog.select().order_by(models.ErrorLog.created.desc()).first()
        self.assertIsNotNone(error_log)
        self.assertEqual(error_log.request_url, "https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11")
        self.assertIsNotNone(error_log.traceback)
        self.assertEqual(api_log.error, error_log.error)
        self.assertIn("Connection to api.privatbank.ua timed out", error_log.error)

        api.HTTP_TIMEOUT = 15


if __name__ == '__main__':
    unittest.main()