#!/usr/bin/env python3
"""hyperloglog — HyperLogLog cardinality estimation. Zero deps."""
import hashlib, math

class HyperLogLog:
    def __init__(self, p=14):
        self.p = p
        self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = self._alpha(self.m)

    def _alpha(self, m):
        if m == 16: return 0.673
        if m == 32: return 0.697
        if m == 64: return 0.709
        return 0.7213 / (1 + 1.079 / m)

    def _hash(self, item):
        h = int(hashlib.sha1(str(item).encode()).hexdigest(), 16)
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
        # Small range correction
        if E <= 2.5 * self.m:
            V = self.registers.count(0)
            if V > 0:
                E = self.m * math.log(self.m / V)
        return int(E)

    def merge(self, other):
        assert self.m == other.m
        result = HyperLogLog(self.p)
        result.registers = [max(a, b) for a, b in zip(self.registers, other.registers)]
        return result

def main():
    import random; random.seed(42)
    for n in [100, 1000, 10000, 100000]:
        hll = HyperLogLog(p=14)
        for i in range(n):
            hll.add(i)
        est = hll.count()
        err = abs(est - n) / n * 100
        print(f"  n={n:>7}: estimate={est:>7}, error={err:.1f}%")
    # With duplicates
    hll2 = HyperLogLog()
    for _ in range(100000):
        hll2.add(random.randint(0, 999))
    print(f"\n  100K inserts, 1K unique: estimate={hll2.count()}")
    # Memory
    print(f"  Memory: {len(hll2.registers)} registers = {len(hll2.registers)}B")

if __name__ == "__main__":
    main()
