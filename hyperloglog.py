#!/usr/bin/env python3
"""HyperLogLog — cardinality estimation with O(1) space."""
import hashlib, math, sys

class HyperLogLog:
    def __init__(self, p=14):
        self.p = p
        self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = self._alpha(self.m)
    @staticmethod
    def _alpha(m):
        if m == 16: return 0.673
        if m == 32: return 0.697
        if m == 64: return 0.709
        return 0.7213 / (1 + 1.079 / m)
    def _hash(self, item):
        return int(hashlib.sha256(str(item).encode()).hexdigest(), 16) & ((1 << 64) - 1)
    def add(self, item):
        h = self._hash(item)
        idx = h >> (64 - self.p)
        w = h << self.p & ((1 << 64) - 1)
        rho = 65 - self.p - w.bit_length() if w else 65 - self.p
        self.registers[idx] = max(self.registers[idx], rho)
    def count(self):
        Z = 1.0 / sum(2.0 ** (-r) for r in self.registers)
        E = self.alpha * self.m * self.m * Z
        if E <= 2.5 * self.m:
            V = self.registers.count(0)
            if V > 0: E = self.m * math.log(self.m / V)
        return int(E + 0.5)
    def merge(self, other):
        for i in range(self.m):
            self.registers[i] = max(self.registers[i], other.registers[i])

if __name__ == "__main__":
    hll = HyperLogLog(10)
    import random; random.seed(42)
    n = 100000
    for i in range(n): hll.add(f"user-{i}")
    est = hll.count()
    err = abs(est - n) / n * 100
    print(f"Actual: {n:,}, Estimated: {est:,}, Error: {err:.1f}%")
