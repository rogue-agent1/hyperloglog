#!/usr/bin/env python3
"""hyperloglog - HyperLogLog cardinality estimation."""
import argparse, hashlib, math, sys

class HyperLogLog:
    def __init__(self, p=14):
        self.p = p; self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = self._alpha()
    def _alpha(self):
        if self.m == 16: return 0.673
        if self.m == 32: return 0.697
        if self.m == 64: return 0.709
        return 0.7213 / (1 + 1.079 / self.m)
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
        indicator = sum(2.0 ** (-r) for r in self.registers)
        estimate = self.alpha * self.m * self.m / indicator
        if estimate <= 2.5 * self.m:
            zeros = self.registers.count(0)
            if zeros > 0: return self.m * math.log(self.m / zeros)
        return estimate
    def merge(self, other):
        for i in range(self.m):
            self.registers[i] = max(self.registers[i], other.registers[i])

def main():
    p = argparse.ArgumentParser(description="HyperLogLog")
    p.add_argument("-n","--items", type=int, default=100000)
    p.add_argument("-p","--precision", type=int, default=14)
    a = p.parse_args()
    hll = HyperLogLog(a.precision)
    for i in range(a.items): hll.add(f"item_{i}")
    est = hll.count()
    error = abs(est - a.items) / a.items * 100
    print(f"Actual: {a.items:,}")
    print(f"Estimated: {est:,.0f}")
    print(f"Error: {error:.2f}%")
    print(f"Memory: {hll.m} registers ({hll.m * 6 // 8} bytes)")
    # Test with duplicates
    hll2 = HyperLogLog(a.precision)
    for i in range(a.items): hll2.add(f"item_{i % 1000}")
    print(f"\n1000 unique (with {a.items} inserts): {hll2.count():,.0f}")

if __name__ == "__main__": main()
