#!/usr/bin/env python3
"""
bell_quantum_simulator.py — from-scratch quantum simulator showing that
|S| = 2√2 emerges directly from the hypersphere geometry of Hilbert space.

NO IMPORTS BEYOND `math`. NO QUANTUM LIBRARIES. Pure arithmetic on
4-dimensional complex amplitude vectors.

WHAT THIS DEMONSTRATES:
  An entangled 2-qubit state lives in ℂ⁴, normalised → unit vector on the
  7-sphere S⁷. Local measurements project this hypersphere structure onto
  ±1 outcomes; the correlation function E(a, b) = ⟨Ψ|A(a) ⊗ B(b)|Ψ⟩
  inherits the hypersphere's cos(Δ) geometry directly.

  CHSH at quantum-optimal axes gives |S| = 2√2 = 2.828... — the Tsirelson
  bound — without any γ-knob, no retrocausal binding by hand, no quantum
  formula imported as a target. The hypersphere does it.

  Compared to a product (separable) state, the CHSH value falls inside the
  classical bound. The difference IS the entanglement.

VOCABULARY:
  - |0⟩, |1⟩: computational basis for one qubit
  - |00⟩, |01⟩, |10⟩, |11⟩: tensor-product basis for two qubits (4 components)
  - |Ψ⁻⟩ = (|01⟩ − |10⟩)/√2: the singlet (canonical entangled state)
  - |+_θ⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩: measurement basis at angle θ
  - A(θ) = |+_θ⟩⟨+_θ| − |−_θ⟩⟨−_θ|: observable with eigenvalues ±1 at angle θ
"""

import math

# ---------- vector / matrix helpers (no numpy) ----------

def matvec(M, v):
    """4×4 matrix times 4-vector."""
    return [sum(M[i][j] * v[j] for j in range(4)) for i in range(4)]


def inner(u, v):
    """⟨u|v⟩ = Σ conj(u_i) v_i  (returns a complex number)."""
    return sum(complex(u[i]).conjugate() * v[i] for i in range(4))


def tensor2(A, B):
    """A ⊗ B for 2×2 matrices → 4×4 matrix."""
    return [[A[i // 2][j // 2] * B[i % 2][j % 2] for j in range(4)] for i in range(4)]


def matsub(A, B):
    """A − B, same-shape 2×2 matrices."""
    return [[A[i][j] - B[i][j] for j in range(len(A[0]))] for i in range(len(A))]


# ---------- quantum primitives ----------

def projector_plus(theta):
    """|+_θ⟩⟨+_θ| where |+_θ⟩ = cos(θ/2)|0⟩ + sin(θ/2)|1⟩."""
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return [[c * c, c * s], [c * s, s * s]]


def projector_minus(theta):
    """|−_θ⟩⟨−_θ| where |−_θ⟩ = −sin(θ/2)|0⟩ + cos(θ/2)|1⟩."""
    c, s = math.cos(theta / 2), math.sin(theta / 2)
    return [[s * s, -c * s], [-c * s, c * c]]


def observable(theta):
    """A(θ) = P_+(θ) − P_−(θ); eigenvalues ±1 along the θ-axis."""
    return matsub(projector_plus(theta), projector_minus(theta))


def bell_singlet():
    """|Ψ⁻⟩ = (|01⟩ − |10⟩)/√2  on basis (|00⟩, |01⟩, |10⟩, |11⟩)."""
    s = 1 / math.sqrt(2)
    return [0 + 0j, s + 0j, -s + 0j, 0 + 0j]


def bell_triplet_phi_plus():
    """|Φ⁺⟩ = (|00⟩ + |11⟩)/√2 — another maximally entangled Bell state."""
    s = 1 / math.sqrt(2)
    return [s + 0j, 0 + 0j, 0 + 0j, s + 0j]


def product_state(theta_a, theta_b):
    """Separable state |+_a⟩ ⊗ |+_b⟩ — no entanglement."""
    a = [math.cos(theta_a / 2) + 0j, math.sin(theta_a / 2) + 0j]
    b = [math.cos(theta_b / 2) + 0j, math.sin(theta_b / 2) + 0j]
    return [a[i // 2] * b[i % 2] for i in range(4)]


# ---------- CHSH machinery ----------

def expectation(state, alice_angle, bob_angle):
    """⟨Ψ| A(a) ⊗ A(b) |Ψ⟩ — joint outcome correlation, ±1 valued observables."""
    M = tensor2(observable(alice_angle), observable(bob_angle))
    return inner(state, matvec(M, state)).real


def chsh(state, a1, a2, b1, b2):
    E11 = expectation(state, a1, b1)
    E12 = expectation(state, a1, b2)
    E21 = expectation(state, a2, b1)
    E22 = expectation(state, a2, b2)
    return E11 - E12 + E21 + E22, [E11, E12, E21, E22]


def state_norm_squared(state):
    """⟨Ψ|Ψ⟩ — should equal 1 for a unit-vector state on S⁷."""
    return inner(state, state).real


def is_entangled(state, tol=1e-9):
    """Check non-separability via Schmidt decomposition rank.
    For 2-qubit state ψ = [ψ00, ψ01, ψ10, ψ11], reshape as 2×2 and
    test if its determinant is non-zero (= entangled)."""
    det = state[0] * state[3] - state[1] * state[2]
    return abs(det) > tol, abs(det)


# ---------- demonstration ----------

def hr(c="=", w=75):
    print(c * w)


def section(title):
    print()
    hr()
    print(title)
    hr()


def main():
    print("Bell-state quantum simulator — hypersphere geometry → |S| = 2√2")
    print("Pure Python, no numpy. The hypersphere does it.")

    # Quantum-optimal CHSH axes (Tsirelson-saturating for the singlet)
    a1, a2 = 0, math.pi / 2
    b1, b2 = math.pi / 4, 3 * math.pi / 4
    tsirelson = 2 * math.sqrt(2)

    section("1. Bell singlet — the hypersphere state")
    state = bell_singlet()
    print(f"  State vector |Ψ⁻⟩ (4 complex amplitudes on S⁷):")
    for i, label in enumerate(["|00⟩", "|01⟩", "|10⟩", "|11⟩"]):
        amp = state[i]
        print(f"    {label} amplitude: {amp.real:+.4f}{amp.imag:+.4f}j")
    print(f"  ⟨Ψ|Ψ⟩ = {state_norm_squared(state):.6f}  (unit norm → on the 7-sphere)")
    ent, det = is_entangled(state)
    print(f"  Entangled? {ent}  (Schmidt determinant = {det:.4f}, ≠ 0)")

    section("2. CHSH on the singlet — Tsirelson bound emerges")
    S, Es = chsh(state, a1, a2, b1, b2)
    print(f"  Axes: a1=0, a2=π/2, b1=π/4, b2=3π/4 (quantum-optimal)")
    for label, e in zip(["E(a1,b1)", "E(a1,b2)", "E(a2,b1)", "E(a2,b2)"], Es):
        print(f"    {label} = {e:+.6f}  (= −cos(Δ) where Δ is angle gap)")
    print(f"  |S| = {abs(S):.6f}")
    print(f"  Target 2√2 = {tsirelson:.6f}")
    match = abs(abs(S) - tsirelson) < 1e-10
    print(f"  Exact saturation: {'✓' if match else '✗'}  (residual = {abs(abs(S) - tsirelson):.2e})")

    section("3. Compare: separable (product) state — classical only")
    sep_state = product_state(0, math.pi / 4)
    print(f"  State |+_0⟩ ⊗ |+_{{π/4}}⟩ (no entanglement)")
    print(f"  ⟨Ψ|Ψ⟩ = {state_norm_squared(sep_state):.6f}")
    ent_sep, det_sep = is_entangled(sep_state)
    print(f"  Entangled? {ent_sep}  (det = {det_sep:.4f})")
    S_sep, _ = chsh(sep_state, a1, a2, b1, b2)
    print(f"  |S| = {abs(S_sep):.6f}  → well inside classical bound of 2")

    section("4. Other entangled state: |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
    triplet = bell_triplet_phi_plus()
    S_t, _ = chsh(triplet, a1, a2, b1, b2)
    print(f"  |S| = {abs(S_t):.6f}")
    print(f"  Same Tsirelson saturation, different basis orientation.")
    print(f"  All maximally-entangled Bell states sit on the hypersphere's")
    print(f"  maximum-correlation equator.")

    section("5. Hypersphere geometry summary")
    print(f"""
  An entangled 2-qubit state is a unit vector in ℂ⁴ = ℝ⁸.
  Modulo global phase, the state space is CP³ ≅ S⁷/U(1).
  Bell states (singlet, |Φ⁺⟩, |Φ⁻⟩, |Ψ⁺⟩) form a tetrahedron on this
  manifold whose vertices saturate the Tsirelson bound.

  When you compute CHSH on such a state:
    • Each E(a, b) = −cos(angular separation in measurement bases)
      (or +cos for triplet — sign convention)
    • All four E values lie on the unit circle, parameterized by angles
    • At quantum-optimal axes (45° pattern), four E values = ±1/√2 with
      reinforcing signs → |S| = 4/√2 = 2√2 EXACTLY.

  The √2 factor isn't imported. It comes from the cos-on-unit-circle
  geometry that the hypersphere imposes. Classical LHV is constrained
  to the inscribed hypercube (|E| ≤ 1 independently with joint-
  distribution constraint); quantum reaches the circumscribed
  hypersphere (E values geometrically linked through Hilbert space).

  This is the 4D object jeff asked about. Built. No quantum library,
  ~150 lines of pure arithmetic, hypersphere structure intact.
  Result: |S| = 2√2 = {tsirelson:.6f}, derived from geometry alone.
""")


if __name__ == "__main__":
    main()
