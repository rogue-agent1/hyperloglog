#!/usr/bin/env python3
"""HyperLogLog — cardinality estimation with O(1) space."""
import sys, hashlib, math, random

class HyperLogLog:
    def __init__(self, p=14):
        self.p = p; self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = 0.7213 / (1 + 1.079 / self.m)
    def _hash(self, item):
        return int(hashlib.sha256(str(item).encode()).hexdigest(), 16)
    def add(self, item):
        h = self._hash(item)
        idx = h & (self.m - 1)
        w = h >> self.p
        self.registers[idx] = max(self.registers[idx], self._leading_zeros(w) + 1)
    def _leading_zeros(self, w):
        if w == 0: return 64 - self.p
        return (64 - self.p) - w.bit_length()
    def count(self):
        raw = self.alpha * self.m**2 / sum(2**(-r) for r in self.registers)
        if raw <= 2.5 * self.m:
            zeros = self.registers.count(0)
            if zeros: return self.m * math.log(self.m / zeros)
        return raw

if __name__ == "__main__":
    hll = HyperLogLog(p=10)
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
    random.seed(42)
    for i in range(n): hll.add(f"item-{random.randint(0, n)}")
    unique_approx = int(hll.count())
    print(f"Added {n} items (many duplicates)")
    print(f"Estimated unique: {unique_approx}")
    print(f"Memory: {hll.m} registers ({hll.m * 6 // 8} bytes)")
    print(f"Error rate: ~{1.04/math.sqrt(hll.m):.1%}")
