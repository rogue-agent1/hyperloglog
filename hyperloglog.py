#!/usr/bin/env python3
"""HyperLogLog — cardinality estimation with O(1) space.

One file. Zero deps. Does one thing well.

Estimates the number of distinct elements in a stream using ~1.6KB of memory
for ~2% standard error. Used in Redis, Presto, BigQuery.
"""
import hashlib, struct, math, sys

class HyperLogLog:
    def __init__(self, p=14):
        """p = precision bits (4-16). Memory = 2^p bytes. Error ≈ 1.04/sqrt(2^p)."""
        assert 4 <= p <= 16
        self.p = p
        self.m = 1 << p
        self.registers = bytearray(self.m)
        self.alpha = self._alpha(self.m)

    @staticmethod
    def _alpha(m):
        if m == 16: return 0.673
        if m == 32: return 0.697
        if m == 64: return 0.709
        return 0.7213 / (1 + 1.079 / m)

    def _hash(self, item):
        if isinstance(item, str): item = item.encode()
        return struct.unpack('<Q', hashlib.sha256(item).digest()[:8])[0]

    def add(self, item):
        h = self._hash(item)
        idx = h & (self.m - 1)
        w = h >> self.p
        rho = 1
        while rho <= 64 - self.p and not (w & 1):
            rho += 1
            w >>= 1
        self.registers[idx] = max(self.registers[idx], rho)

    def count(self):
        """Estimate cardinality."""
        indicator = sum(2.0 ** (-r) for r in self.registers)
        estimate = self.alpha * self.m * self.m / indicator
        # Small range correction
        if estimate <= 2.5 * self.m:
            zeros = self.registers.count(0)
            if zeros > 0:
                estimate = self.m * math.log(self.m / zeros)
        # Large range correction (64-bit hash)
        elif estimate > (1 << 32) / 30.0:
            estimate = -(1 << 64) * math.log(1 - estimate / (1 << 64))
        return int(estimate)

    def merge(self, other):
        """Merge another HLL (union)."""
        assert self.p == other.p
        result = HyperLogLog(self.p)
        for i in range(self.m):
            result.registers[i] = max(self.registers[i], other.registers[i])
        return result

    def error(self):
        return 1.04 / math.sqrt(self.m)

def main():
    hll = HyperLogLog(p=14)
    print(f"HyperLogLog (p={hll.p}, m={hll.m}, memory={hll.m}B, error≈{hll.error():.2%})\n")
    for n in [100, 1000, 10000, 100000]:
        h = HyperLogLog(p=14)
        for i in range(n):
            h.add(f"item-{i}")
        est = h.count()
        err = abs(est - n) / n * 100
        print(f"  n={n:>7,d}  est={est:>7,d}  error={err:.1f}%")
    # Merge demo
    h1, h2 = HyperLogLog(12), HyperLogLog(12)
    for i in range(5000): h1.add(f"a-{i}")
    for i in range(3000, 8000): h2.add(f"a-{i}")
    merged = h1.merge(h2)
    print(f"\nMerge: |A|≈{h1.count()}, |B|≈{h2.count()}, |A∪B|≈{merged.count()} (actual=8000)")

if __name__ == "__main__":
    main()
