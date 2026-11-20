# O25 regression baseline

`legacy_o25_reference.npz` records the output of the Python implementation as
received in the repository snapshot. It uses one deterministic hyperspectral
spectrum from 350 to 800 nm and a correction from `(30, 45, 90)` to `(0, 0, 0)`.

This fixture is a change detector, not evidence of MATLAB equivalence. A later
validation layer will compare the rebuilt Python implementation directly with
the authoritative MATLAB O25 and BH4 references.
