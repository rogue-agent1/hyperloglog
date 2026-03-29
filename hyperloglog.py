#!/usr/bin/env python3
"""HyperLogLog — cardinality estimation."""
import hashlib, math, sys

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
        Z = 1.0 / sum(2.0**(-r) for r in self.registers)
        E = self.alpha * self.m * self.m * Z
        if E <= 2.5 * self.m:
            V = self.registers.count(0)
            if V > 0: E = self.m * math.log(self.m / V)
        return int(E)

if __name__ == "__main__":
    hll = HyperLogLog()
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    for i in range(n):
        hll.add(i)
    est = hll.count()
    err = abs(est - n) / n * 100
    print(f"Added {n} unique items, estimated: {est} (error: {err:.1f}%)")
