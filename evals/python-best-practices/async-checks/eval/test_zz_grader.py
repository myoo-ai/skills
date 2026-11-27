import asyncio
import time
import unittest

from probes.checker import check_all


async def probe(host):
    if host == "fast.example.com":
        await asyncio.sleep(0.05)
        return True
    if host == "slow.example.com":
        await asyncio.sleep(10)
        return True
    if host == "down.example.com":
        raise ConnectionError("connection refused")
    return False


class GraderTest(unittest.IsolatedAsyncioTestCase):
    async def test_check_all(self):
        calls = []

        async def counting(host):
            calls.append(host)
            return await probe(host)

        hosts = ["FAST.example.com", "https://fast.example.com/", "slow.example.com", "down.example.com", "bad.example.com"]
        start = time.monotonic()
        with self.assertLogs("probes.checker", "WARNING") as logs:
            got = await check_all(hosts, counting, timeout=0.3)
        self.assertLess(time.monotonic() - start, 2)
        self.assertEqual(got, {"fast.example.com": True, "slow.example.com": False, "down.example.com": False, "bad.example.com": False})
        self.assertEqual(sorted(calls), sorted(set(calls)))
        self.assertTrue(any("down.example.com" in line for line in logs.output), logs.output)

    async def test_runs_concurrently(self):
        async def sleepy(host):
            await asyncio.sleep(0.3)
            return True

        start = time.monotonic()
        got = await check_all([f"h{i}.example.com" for i in range(10)], sleepy, timeout=2)
        self.assertLess(time.monotonic() - start, 1.5)
        self.assertEqual(len(got), 10)
        self.assertTrue(all(got.values()))
