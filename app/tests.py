import unittest

import api.test_api as test_api
import models
import api.privatbank_api as privatbank_api
import api.nbu_api as nbu_api

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

    def test_privat(self):
        xrate = models.XRate.get(id = 1)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 20)
        privatbank_api.Api().update_rate(840, 980)
        xrate = models.XRate.get(id = 1)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 25)
        self.assertGreater(updated_after, updated_before)

    def test_nbu(self):
        xrate = models.XRate.get(from_currency = 978, to_currency = 980)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 45)
        nbu_api.Api().update_rate(978, 980)
        xrate = models.XRate.get(from_currency = 978, to_currency = 980)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 50)
        self.assertGreater(updated_after, updated_before)

if __name__ == '__main__':
    unittest.main()