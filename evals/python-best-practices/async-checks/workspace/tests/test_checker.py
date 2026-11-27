import unittest

from probes.checker import normalize_host


class NormalizeHostTest(unittest.TestCase):
    def test_normalize(self):
        cases = {
            "API.Example.com": "api.example.com",
            "https://shop.example.com:8443/health": "shop.example.com",
            "cdn.example.com.": "cdn.example.com",
        }
        for raw, want in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(normalize_host(raw), want)


if __name__ == "__main__":
    unittest.main()
