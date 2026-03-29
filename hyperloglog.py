#!/usr/bin/env python3
"""HyperLogLog for cardinality estimation."""
import sys, hashlib, math

class HyperLogLog:
    def __init__(self, p=14):
        self.p = p
        self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m)
    def _hash(self, item):
        return int(hashlib.sha256(str(item).encode()).hexdigest(), 16)
    def add(self, item):
        h = self._hash(item)
        idx = h & (self.m - 1)
        w = h >> self.p
        self.registers[idx] = max(self.registers[idx], self._rho(w))
    def _rho(self, w):
        if w == 0: return 64 - self.p
        return (w & -w).bit_length()
    def count(self):
        z = 1.0 / sum(2.0**(-r) for r in self.registers)
        e = self.alpha * self.m * self.m * z
        if e <= 2.5 * self.m:
            v = self.registers.count(0)
            if v > 0:
                e = self.m * math.log(self.m / v)
        return int(e)
    def merge(self, other):
        for i in range(self.m):
            self.registers[i] = max(self.registers[i], other.registers[i])

def test():
    hll = HyperLogLog(10)
    for i in range(10000):
        hll.add(f"item{i}")
    est = hll.count()
    assert 8000 < est < 12000, f"Expected ~10000, got {est}"
    # Duplicates shouldn't increase count much
    for i in range(5000):
        hll.add(f"item{i}")
    est2 = hll.count()
    assert 8000 < est2 < 12000
    # Merge
    hll2 = HyperLogLog(10)
    for i in range(10000, 15000):
        hll2.add(f"item{i}")
    hll.merge(hll2)
    est3 = hll.count()
    assert 12000 < est3 < 18000
    print("  hyperloglog: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else: print("HyperLogLog cardinality estimator")
