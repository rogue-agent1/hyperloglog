#!/usr/bin/env python3
"""HyperLogLog - Estimate unique element count using O(log log n) space."""
import sys, hashlib, math

class HyperLogLog:
    def __init__(self, p=14):
        self.p = p; self.m = 1 << p; self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m) if self.m >= 128 else {16:0.673,32:0.697,64:0.709}.get(self.m, 0.7213)
    def _hash(self, item):
        return int(hashlib.sha256(str(item).encode()).hexdigest(), 16) & ((1 << 64) - 1)
    def add(self, item):
        h = self._hash(item); idx = h & (self.m - 1); w = h >> self.p
        self.registers[idx] = max(self.registers[idx], self._rho(w))
    def _rho(self, w):
        if w == 0: return 64 - self.p
        return min(64 - self.p, (w & -w).bit_length())
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
    import random; random.seed(42)
    print("=== HyperLogLog ===\n")
    for n in [100, 1000, 10000, 100000]:
        hll = HyperLogLog(p=14)
        for _ in range(n): hll.add(random.randint(0, n * 10))
        est = hll.count()
        actual = n  # approximate since random with replacement
        err = abs(est - actual) / actual * 100
        print(f"  Added {n:>7d} items: estimate={est:>7d} error={err:.1f}%  memory={hll.m * 6 // 8} bytes")

if __name__ == "__main__":
    main()
