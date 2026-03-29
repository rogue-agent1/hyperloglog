#!/usr/bin/env python3
"""hyperloglog - HyperLogLog cardinality estimator."""
import sys, json, hashlib, math

class HyperLogLog:
    def __init__(self, p=14):
        self.p = p; self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m)
    
    def _hash(self, item):
        h = int(hashlib.sha256(str(item).encode()).hexdigest(), 16)
        return h & ((1 << 64) - 1)
    
    def add(self, item):
        h = self._hash(item)
        idx = h & (self.m - 1)
        w = h >> self.p
        self.registers[idx] = max(self.registers[idx], self._rho(w))
    
    def _rho(self, w):
        if w == 0: return 64 - self.p + 1
        return (64 - self.p) - w.bit_length() + 1
    
    def count(self):
        Z = 1.0 / sum(2.0 ** (-r) for r in self.registers)
        E = self.alpha * self.m * self.m * Z
        if E <= 2.5 * self.m:
            V = self.registers.count(0)
            if V > 0: E = self.m * math.log(self.m / V)
        return int(E)
    
    def merge(self, other):
        for i in range(self.m):
            self.registers[i] = max(self.registers[i], other.registers[i])

def main():
    print("HyperLogLog demo\n")
    for n in [100, 1000, 10000, 100000]:
        hll = HyperLogLog(p=14)
        for i in range(n): hll.add(f"item_{i}")
        est = hll.count()
        err = abs(est - n) / n * 100
        print(f"  n={n:>6d}: estimate={est:>6d}, error={err:.1f}%")
    # Merge test
    h1 = HyperLogLog(); h2 = HyperLogLog()
    for i in range(5000): h1.add(f"a_{i}")
    for i in range(3000, 8000): h2.add(f"a_{i}")
    h1.merge(h2)
    print(f"\n  Merge (5k+5k, 3k overlap): estimate={h1.count()} (true=8000)")

if __name__ == "__main__":
    main()
