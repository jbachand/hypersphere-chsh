# hypersphere-chsh

Companion code for the paper **"The Hypersphere Does It: $|S| = p\sqrt{8}$ from Werner-State Density-Matrix Algebra"** (Bachand 2026).

Four self-contained Python scripts (~700 lines total, zero external dependencies) that derive the full range of CHSH values $|S| \in [0, 2\sqrt{2}]$ from elementary 4×4 complex matrix arithmetic. See [`paper.pdf`](paper.pdf) for the full paper.

## The master equation

For a Werner state $\rho_W(p) = p\,|\Psi^-\rangle\langle\Psi^-| + (1-p)\,I/4$, the CHSH value at the optimal axes is

$$|S| = p\sqrt{8}$$

Special cases:
- $p = 0$ (maximally mixed): $|S| = 0$
- $p = 1/\sqrt{2}$ (Bell-violation threshold): $|S| = 2$ (classical Bell bound)
- $p = 1$ (pure Bell singlet): $|S| = 2\sqrt{2}$ (Tsirelson bound)

The $\sqrt{8}$ factor is the geometric projection of the Bell singlet onto the optimal CHSH coordinate axes in the 4D correlation space. This relation is algebraically identical to the standard Werner-CHSH form $|S| = 2\sqrt{2}\,p$ (Werner 1989; Horodecki et al. 1995); the single-radical rewrite makes the geometric origin transparent.

## Run the demonstrations

Requires Python 3.x. No `pip install` step — only the standard library.

```bash
python3 incremental_counter_chsh.py    # §3.1 — shared-state classical counter   |S| ≈ 2.001
python3 zipper_counter_chsh.py         # §3.2 — deterministic zipper             |S| = 2.00000 exact
python3 fourd_chsh.py                  # §3.3 — Werner γ-knob (density matrix)   |S|: 2.0 → 2√2
python3 bell_quantum_simulator.py      # §3.4 — from-scratch hypersphere sim     |S| = 2.828427
```

Total runtime: ~10 seconds end-to-end on a modern laptop.

## Building the paper

The PDF is precompiled (`paper.pdf`). To rebuild from `paper.md`:

```bash
./build_paper.sh
```

Requires:
- `python3` (any 3.x)
- `pandoc` (`brew install pandoc`)
- `tectonic` (`brew install tectonic`)

The script uses `typeset_math.py` (path adjustable) to convert backtick spans to LaTeX math, then pipes through pandoc → tectonic.

## Contents

| File | Description |
|---|---|
| `paper.md` | Paper source (Markdown with LaTeX math) |
| `paper.pdf` | Compiled paper (7 pages, ~75 KB) |
| `build_paper.sh` | PDF build script (Markdown → LaTeX → PDF) |
| `incremental_counter_chsh.py` | §3.1 demo (~150 lines) |
| `zipper_counter_chsh.py` | §3.2 demo (~200 lines) |
| `fourd_chsh.py` | §3.3 demo (~200 lines) |
| `bell_quantum_simulator.py` | §3.4 demo (~150 lines) |
| `LICENSE` | MIT license for code; paper under CC-BY 4.0 |

## Citation

```bibtex
@article{bachand2026hypersphere,
  title  = {The Hypersphere Does It: $|S| = p\sqrt{8}$ from Werner-State Density-Matrix Algebra},
  author = {Bachand, Jeff},
  year   = {2026},
  note   = {Code: https://github.com/jbachand/hypersphere-chsh}
}
```

## Scope

This paper is a pedagogical/interpretive contribution. The relation $|S| = p\sqrt{8}$ is a theorem of standard quantum mechanics applied to the Werner state (Werner 1989; Horodecki et al. 1995); we do not claim new physics or new mathematics. The contribution is:

1. A single compact expression that unifies the classical Bell bound, the Werner threshold, and the Tsirelson bound as values of one linear function
2. A geometric reading of the $\sqrt{8}$ constant as the singlet's projection onto CHSH axes
3. Four self-contained, zero-dependency, reproducible Python demonstrations across the full $|S| \in [0, 2\sqrt{2}]$ spectrum

See §4 of the paper for what the framework does and does *not* claim.

## License

- Code: MIT License (see [`LICENSE`](LICENSE))
- Paper: CC-BY 4.0
