#!/usr/bin/env python3
"""
zipper_counter_chsh.py — jeff's "linear zipper" extension of the shared-counter
test, FAST version.

SETUP:
  Function A is FAST on odd N, SLOW on even N (10× ratio)
  Function B is FAST on even N, SLOW on odd N
  Both race; faster one advances N. Each function only ever completes its
  fast steps. Joint system advances at the FAST rate (no slow steps).

KEY OPTIMIZATION:
  Simulate each trial's zipper ONCE, then evaluate CHSH for any axis pair
  by lookup on the pre-computed (event_time, N) trajectory. This makes
  axis search ~1000× faster than re-simulating per axis pair.
"""

import random
from itertools import product

FAST_TIME = 1.0
SLOW_TIME = 10.0
JITTER = 0.05
TARGET_N = 30          # advance counter to this value
N_TRIALS = 5000        # trials for CHSH (one zipper sim per trial)
N_TRIALS_SPEEDUP = 200


def simulate_zipper_fast(seed, target_n=TARGET_N):
    """Returns parallel arrays (event_times, N_after_each_event).
    Each trial is one full deterministic simulation given the random seed."""
    rng = random.Random(seed)
    t = 0.0
    N = 0
    times = []
    while N < target_n:
        # A fast on odd N, slow on even N; B is complementary
        a_base = FAST_TIME if (N % 2 == 1) else SLOW_TIME
        b_base = FAST_TIME if (N % 2 == 0) else SLOW_TIME
        a_time = a_base * (1 + (rng.random() - 0.5) * 2 * JITTER)
        b_time = b_base * (1 + (rng.random() - 0.5) * 2 * JITTER)
        dt = a_time if a_time <= b_time else b_time
        t += dt
        N += 1
        times.append(t)
    return times  # times[k-1] = time when N became k


def simulate_solo_A(seed, target_n=TARGET_N):
    """A running alone: pays slow on every even N, fast on every odd N."""
    rng = random.Random(seed)
    t = 0.0
    for N in range(target_n):
        a_base = FAST_TIME if (N % 2 == 1) else SLOW_TIME
        t += a_base * (1 + (rng.random() - 0.5) * 2 * JITTER)
    return t


def N_at(times, query_t):
    """Return N at query_t given event times. Binary search."""
    lo, hi = 0, len(times)
    while lo < hi:
        mid = (lo + hi) // 2
        if times[mid] <= query_t:
            lo = mid + 1
        else:
            hi = mid
    return lo  # number of events that have occurred by query_t


def speedup_test():
    print("=" * 75)
    print("Part 1: SPEEDUP TEST (zipper joint vs solo-A)")
    print("=" * 75)
    print(f"  FAST_TIME={FAST_TIME}, SLOW_TIME={SLOW_TIME} (ratio {SLOW_TIME/FAST_TIME:.0f}×)")
    print(f"  TARGET_N={TARGET_N}, trials={N_TRIALS_SPEEDUP}")

    zipper_times = []
    solo_times = []
    for seed in range(N_TRIALS_SPEEDUP):
        times = simulate_zipper_fast(seed)
        zipper_times.append(times[-1])
        solo_times.append(simulate_solo_A(seed + 1_000_000))

    avg_z = sum(zipper_times) / len(zipper_times)
    avg_s = sum(solo_times) / len(solo_times)
    expected_solo = TARGET_N * (FAST_TIME + SLOW_TIME) / 2
    expected_zipper = TARGET_N * FAST_TIME
    expected_speedup = (FAST_TIME + SLOW_TIME) / (2 * FAST_TIME)

    print(f"\n  Solo A    measured: {avg_s:.2f}   (theory: {expected_solo:.2f})")
    print(f"  Zipper    measured: {avg_z:.2f}   (theory: {expected_zipper:.2f})")
    print(f"  Speedup   measured: {avg_s/avg_z:.3f}× (theory: {expected_speedup:.3f}×)")
    print(f"\n  >>> Joint zipper advances at the FAST rate.")
    print(f"      A and B each only complete their easy halves.")
    print(f"      From each function's local log, every problem it finished was easy.")


def chsh_cached(times_list, a1, a2, b1, b2):
    """Compute S = E(a1,b1) - E(a1,b2) + E(a2,b1) + E(a2,b2) over cached trials."""
    n = len(times_list)
    sum_ab = [0, 0, 0, 0]
    pairs = [(a1, b1), (a1, b2), (a2, b1), (a2, b2)]
    for times in times_list:
        for k, (a, b) in enumerate(pairs):
            n_a = N_at(times, a)
            n_b = N_at(times, b)
            out_a = 1 if (n_a % 2 == 0) else -1
            out_b = 1 if (n_b % 2 == 0) else -1
            sum_ab[k] += out_a * out_b
    E = [s / n for s in sum_ab]
    S = E[0] - E[1] + E[2] + E[3]
    return S, E


def chsh_test():
    print()
    print("=" * 75)
    print("Part 2: CHSH on the zipper")
    print("=" * 75)
    print(f"  Pre-simulating {N_TRIALS} trials (cached for all axis search)...")
    times_list = [simulate_zipper_fast(seed) for seed in range(N_TRIALS)]
    # Find max event time across trials to set search range
    max_t = max(times[-1] for times in times_list)
    print(f"  Trials simulated. Max trial end time: {max_t:.2f}")

    # Split grid into Alice's set (odd-indexed) and Bob's set (even-indexed)
    # so a1, a2 ∈ Alice_grid and b1, b2 ∈ Bob_grid with disjoint sets —
    # this is the proper Bell-test setup where Alice and Bob measure
    # at different times (not the same time).
    grid_n = 24
    full_grid = [1 + i * (max_t * 0.95 - 1) / (grid_n - 1) for i in range(grid_n)]
    alice_grid = full_grid[::2]
    bob_grid = full_grid[1::2]
    print(f"  Alice's grid (a1, a2 chosen from): {[round(x,2) for x in alice_grid]}")
    print(f"  Bob's   grid (b1, b2 chosen from): {[round(x,2) for x in bob_grid]}")

    best_S = 0
    best_axes = None
    n_pairs = 0
    for a1, a2 in product(alice_grid, repeat=2):
        if a2 <= a1:
            continue
        for b1, b2 in product(bob_grid, repeat=2):
            if b2 <= b1:
                continue
            S, _ = chsh_cached(times_list, a1, a2, b1, b2)
            n_pairs += 1
            if abs(S) > abs(best_S):
                best_S = S
                best_axes = (a1, a2, b1, b2)

    print(f"  Searched {n_pairs} axis combinations at N={N_TRIALS}")
    print(f"  max |S| = {abs(best_S):.4f} at axes {tuple(round(x, 2) for x in best_axes)}")

    # Confirm at higher N with multiple seed batches
    print(f"\n  Confirming best axes with 3 independent trial batches (N={N_TRIALS} each):")
    S_values = []
    for batch_id, seed_offset in enumerate([0, 100000, 200000]):
        batch = [simulate_zipper_fast(seed + seed_offset) for seed in range(N_TRIALS)]
        S, E = chsh_cached(batch, *best_axes)
        S_values.append(S)
        print(f"    batch {batch_id+1}: S = {S:+.5f}  |S| = {abs(S):.5f}  "
              f"E={tuple(round(e, 3) for e in E)}")
    mean_S = sum(abs(s) for s in S_values) / len(S_values)
    spread = max(abs(s) for s in S_values) - min(abs(s) for s in S_values)
    print(f"    mean |S| = {mean_S:.5f}, spread = {spread:.5f}")
    print(f"    gap from 2.0: {2 - mean_S:+.5f}")

    print()
    if mean_S > 2 + spread:
        print(f"  >>> Apparent |S|>2 — noise inflation (Bell forbids real violation).")
    elif abs(mean_S - 2) < max(spread, 0.01):
        print(f"  >>> |S| ≈ 2.0 — SATURATES the classical bound.")
        print(f"      Zipper architecture (shared state + complementary specialization)")
        print(f"      hits the same classical ceiling as the trivial shared counter")
        print(f"      and the π universe's chain. The √2 gap to quantum is still")
        print(f"      structurally inaccessible to any classical system.")
    else:
        print(f"  >>> |S| = {mean_S:.4f} < 2 — does not saturate.")


def main():
    speedup_test()
    chsh_test()


if __name__ == "__main__":
    main()
