#!/usr/bin/env python3
"""
incremental_counter_chsh.py — empirical CHSH test on jeff's shared-counter
thought experiment.

SETUP:
  Two functions share a global state N.
  Function A increments N by 1 every 1 unit of time.
  Function B increments N by 1 every 10 units of time.
  Hidden variable: B's phase offset φ ∈ [0, 10), random per trial.

  N(t, φ) = (# of A-ticks at time ≤ t) + (# of B-ticks at time ≤ t given phase φ)

CHSH:
  Alice picks setting a ∈ {a_1, a_2} = a sampling time.
  Bob picks setting b ∈ {b_1, b_2} = a different sampling time.
  Outcome A(a, φ) = +1 if N(a, φ) is even, -1 if odd.
  Outcome B(b, φ) = +1 if N(b, φ) is even, -1 if odd.

  E(a, b) = ⟨A(a, φ) · B(b, φ)⟩ averaged over random φ.
  S = E(a_1, b_1) - E(a_1, b_2) + E(a_2, b_1) + E(a_2, b_2).

PREDICTION:
  Bell's theorem forces |S| ≤ 2 (this is a classical LHV system).
  Question: does it saturate at 2 (like the π universe), or land < 2?
"""

import random
import math
from itertools import product

TOTAL_TIME = 100  # simulation horizon, units of time
N_TRIALS = 100000  # random φ draws per (setting_A, setting_B) pair


def N_at(query_t, phase_b):
    """N(query_t, phase_b) — count of A-ticks + B-ticks at time ≤ query_t."""
    # A ticks at t = 1, 2, 3, ... (we say A's first tick at t=1)
    n_A = max(0, int(math.floor(query_t)))
    # B ticks at t = phase_b, phase_b+10, phase_b+20, ...
    if query_t < phase_b:
        n_B = 0
    else:
        n_B = 1 + int(math.floor((query_t - phase_b) / 10))
    return n_A + n_B


def outcome(setting, phase_b):
    """±1 outcome: parity of N at the chosen sampling time."""
    n = N_at(setting, phase_b)
    return 1 if (n % 2 == 0) else -1


def expectation(setting_a, setting_b, n_trials, seed):
    """E(a, b) = ⟨A(a, φ) · B(b, φ)⟩ averaged over random φ."""
    rng = random.Random(seed)
    total = 0
    for _ in range(n_trials):
        phase_b = rng.uniform(0, 10)
        prod = outcome(setting_a, phase_b) * outcome(setting_b, phase_b)
        total += prod
    return total / n_trials


def chsh(a1, a2, b1, b2, n_trials, seed=0xABCD):
    """S = E(a1, b1) - E(a1, b2) + E(a2, b1) + E(a2, b2)."""
    E_a1b1 = expectation(a1, b1, n_trials, seed)
    E_a1b2 = expectation(a1, b2, n_trials, seed + 1)
    E_a2b1 = expectation(a2, b1, n_trials, seed + 2)
    E_a2b2 = expectation(a2, b2, n_trials, seed + 3)
    return E_a1b1 - E_a1b2 + E_a2b1 + E_a2b2, (E_a1b1, E_a1b2, E_a2b1, E_a2b2)


def search_max_chsh(setting_range, n_trials=2000, n_grid=20):
    """Coarse grid search over (a1, a2, b1, b2) to maximize |S|."""
    settings = [setting_range[0] + i * (setting_range[1] - setting_range[0]) / (n_grid - 1)
                for i in range(n_grid)]
    best_S = 0
    best_axes = None
    n_tested = 0
    for a1, a2 in product(settings, repeat=2):
        if a2 <= a1:
            continue
        for b1, b2 in product(settings, repeat=2):
            if b2 <= b1:
                continue
            S, _ = chsh(a1, a2, b1, b2, n_trials, seed=hash((a1, a2, b1, b2)) & 0xFFFFFFFF)
            n_tested += 1
            if abs(S) > abs(best_S):
                best_S = S
                best_axes = (a1, a2, b1, b2)
    return best_S, best_axes, n_tested


def main():
    print("=" * 75)
    print("CHSH test on shared-counter system")
    print("=" * 75)
    print(f"  A rate: 1 increment / sec")
    print(f"  B rate: 1 increment / 10 sec")
    print(f"  Hidden variable: B phase offset φ ∈ [0, 10)")
    print(f"  Outcome: parity of N at the chosen sampling time (±1)")
    print(f"  Total simulation time: {TOTAL_TIME} units")
    print(f"  N trials per E(a, b): {N_TRIALS}")
    print()

    # Stage 1: coarse axis search at LOW N (just to identify candidates)
    print("Stage 1: coarse axis search over [1, 99] (30-point grid, N=2000)")
    print("-" * 75)
    best_S, best_axes, n_tested = search_max_chsh((1, 99), n_trials=2000, n_grid=30)
    print(f"  tested {n_tested} axis combinations")
    print(f"  inflated max |S| = {abs(best_S):.4f} (multiple-testing noise at low N)")
    print(f"  best axes (a1, a2, b1, b2) = {best_axes}")
    print()

    # Stage 2: refine and re-test at high N
    a1, a2, b1, b2 = best_axes
    print(f"Stage 2: re-test best axes at N={N_TRIALS} for 3 different seeds")
    print("-" * 75)
    print(f"  axes: a1={a1:.4f}, a2={a2:.4f}, b1={b1:.4f}, b2={b2:.4f}")
    S_values = []
    for seed in [0x1234, 0x5678, 0x9ABC]:
        S_refined, E_vals = chsh(a1, a2, b1, b2, N_TRIALS, seed=seed)
        S_values.append(S_refined)
        E_a1b1, E_a1b2, E_a2b1, E_a2b2 = E_vals
        print(f"  seed 0x{seed:04X}: S = {S_refined:+.5f}  |S| = {abs(S_refined):.5f}")
        print(f"           E(a1,b1)={E_a1b1:+.4f}  E(a1,b2)={E_a1b2:+.4f}  "
              f"E(a2,b1)={E_a2b1:+.4f}  E(a2,b2)={E_a2b2:+.4f}")
    mean_S = sum(abs(s) for s in S_values) / len(S_values)
    spread_S = max(abs(s) for s in S_values) - min(abs(s) for s in S_values)
    print(f"  mean |S|: {mean_S:.5f}")
    print(f"  spread:   {spread_S:.5f}")
    print(f"  gap from 2.0: {2 - mean_S:+.5f}")
    print()
    S_refined = sum(S_values) / len(S_values)  # use mean for final verdict

    # Verdict
    print("=" * 75)
    print("VERDICT")
    print("=" * 75)
    sem_S = spread_S / 2  # rough proxy for measurement uncertainty
    gap = 2 - abs(S_refined)
    if abs(S_refined) > 2 + sem_S:
        print(f"  |S| > 2 + spread — APPARENT VIOLATION (almost certainly noise inflation).")
    elif gap < sem_S:
        print(f"  |S| = {abs(S_refined):.5f}, within measurement spread of 2.0")
        print(f"  → SATURATES classical Bell bound (consistent with |S| = 2 exactly).")
        print(f"  Shared-state architecture reaches maximum classical correlation —")
        print(f"  parallel to the π universe's chain (|S| = 2.0000 in May 2026 test).")
    else:
        print(f"  |S| = {abs(S_refined):.5f} < 2, gap = {gap:.5f} ({gap/sem_S:.1f}× spread)")
        print(f"  → DOES NOT saturate; sits inside the classical region.")
        print(f"  Shared state correlates strongly but not at the classical ceiling.")
    print()
    print("  Bell's theorem forced |S| ≤ 2; the empirical value tells us where")
    print("  this specific shared-state architecture sits within the classical region.")


if __name__ == "__main__":
    main()
