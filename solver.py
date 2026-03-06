from __future__ import annotations
from functools import lru_cache
import time
from typing import List, Tuple, Optional

def _canonical(nums: List[int]) -> Tuple[int, ...]:
    return tuple(sorted(nums))

def _candidates(a: int, b: int):
    # + and * always valid (positive integers)
    yield a + b, f"{a} + {b} = {a + b}"
    yield a * b, f"{a} * {b} = {a * b}"

    # subtraction only if positive
    if a > b:
        yield a - b, f"{a} - {b} = {a - b}"
    elif b > a:
        yield b - a, f"{b} - {a} = {b - a}"

    # division only if exact and positive
    if b != 0 and a % b == 0:
        q = a // b
        if q > 0:
            yield q, f"{a} / {b} = {q}"
    if a != 0 and b % a == 0:
        q = b // a
        if q > 0:
            yield q, f"{b} / {a} = {q}"

def find_solution(numbers: List[int], target: int, time_limit: float = 2.0) -> Optional[List[str]]:
    start = time.time()
    initial = _canonical(numbers)

    @lru_cache(maxsize=None)
    def dfs(state: Tuple[int, ...]) -> Optional[Tuple[str, ...]]:
        if time.time() - start > time_limit:
            return None

        if len(state) == 1:
            return tuple() if state[0] == target else None

        n = len(state)
        for i in range(n):
            for j in range(i + 1, n):
                a, b = state[i], state[j]
                rest = list(state[:i] + state[i + 1:j] + state[j + 1:])

                for val, step in _candidates(a, b):
                    if val <= 0:
                        continue
                    new_state = _canonical(rest + [val])
                    sub = dfs(new_state)
                    if sub is not None:
                        return (step,) + sub
        return None

    res = dfs(initial)
    return list(res) if res is not None else None
