import unittest

import test_api
import models
import privatbank_api
import nbu_api

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
        privatbank_api.update_xrates(840, 980)
        xrate = models.XRate.get(id = 1)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 25)
        self.assertGreater(updated_after, updated_before)

    def test_nbu(self):
        xrate = models.XRate.get(from_currency = 978, to_currency = 980)
        updated_before = xrate.updated
        self.assertEqual(xrate.rate, 45)
        nbu_api.update_xrates(978, 980)
        xrate = models.XRate.get(from_currency = 978, to_currency = 980)
        updated_after = xrate.updated

        self.assertGreater(xrate.rate, 50)
        self.assertGreater(updated_after, updated_before)

if __name__ == '__main__':
    unittest.main()