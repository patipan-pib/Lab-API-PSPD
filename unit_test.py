import unittest
from app.main import app   # ปรับ path ให้ตรงกับโครงสร้างโปรเจกต์

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_getcode(self):
        res = self.app.get('/getcode')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {"code": "success"})

    def test_plus_ok(self):
        res = self.app.get('/plus/5/7')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {'result': 12})

    def test_is_prime_true(self):
        res = self.app.get('/is_prime/19')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["is_prime"], True)

    def test_is_prime_false(self):
        res = self.app.get('/is_prime/20')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json()["is_prime"], False)

    def test_primes_range(self):
        res = self.app.get('/primes?start=10&end=20')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["primes"], [11, 13, 17, 19])
    
    def test_x_is_1(self):
        res = self.app.get('/next5/1')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {'result': 6})
    
    def test_x_is_neg10(self):
        res = self.app.get('/next5/-10')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {'result': -5})

    def test_x_is_1dot5(self):
        res = self.app.get('/next5/1.5')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), {'result': 6.5})
        

if __name__ == "__main__":
    unittest.main()


# python -m unittest unit_test.py -v