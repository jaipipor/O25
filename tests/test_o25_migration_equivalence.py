"""Independent equivalence of the procedural and class-based O25 cores."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pytest

import o25
from o25.model import O25Model
from tests.reference.procedural_o25 import O25_hyp as procedural_o25


@dataclass(frozen=True)
class Case:
    case_id: str
    wl: np.ndarray
    Rrs: np.ndarray
    g0: tuple[float, float, float]
    g1: tuple[float, float, float]


def _shape(wl: np.ndarray, kind: str) -> np.ndarray:
    x = (wl - 560.0) / 150.0
    if kind == "blue":
        r = 0.0018 + 0.0075 * np.exp(-((wl - 445.0) / 115.0) ** 2)
    elif kind == "green":
        r = 0.0015 + 0.0080 * np.exp(-((wl - 555.0) / 95.0) ** 2)
    elif kind == "red":
        r = 0.0020 + 0.0030 * (x - x.min()) / (x.max() - x.min())
    elif kind == "low":
        r = 0.00035 + 0.0011 * np.exp(-((wl - 520.0) / 125.0) ** 2)
    else:  # pragma: no cover
        raise ValueError(kind)
    return np.asarray(r, dtype=np.float64)


def _deterministic_cases() -> list[Case]:
    grids = {
        "four": np.array([443.0, 490.0, 560.0, 665.0]),
        "olci12": np.array([400., 412., 443., 490., 510., 560., 620., 665., 673., 681., 709., 753.]),
        "hyper": np.arange(350.0, 801.0),
    }
    geometries = {
        "to_zero": ((30., 20., 120.), (0., 0., 0.)),
        "off_node": ((63.24, 45., 120.), (0., 0., 0.)),
        "arbitrary": ((30., 20., 120.), (40., 10., 75.)),
    }
    cases = []
    for grid_name, wl in grids.items():
        for shape_name in ("blue", "green", "red", "low"):
            for geometry_name, (g0, g1) in geometries.items():
                cases.append(Case(
                    f"{grid_name}-{shape_name}-{geometry_name}",
                    wl, _shape(wl, shape_name), g0, g1,
                ))
    return cases


def _edge_cases() -> list[Case]:
    wl = np.arange(350.0, 801.0)
    r = _shape(wl, "green")
    pairs = [
        ("identity_node", (30., 20., 120.), (30., 20., 120.)),
        ("identity_off_node", (63.24, 45., 127.5), (63.24, 45., 127.5)),
        ("lower_boundary", (0., 0., 0.), (0., 0., 0.)),
        ("upper_boundary", (87.5, 87.5, 180.), (0., 0., 0.)),
        ("zero_sza", (0., 30., 120.), (20., 10., 45.)),
        ("zero_vza", (30., 0., 120.), (20., 10., 45.)),
    ]
    return [Case(name, wl, r, g0, g1) for name, g0, g1 in pairs]


def _random_cases() -> list[Case]:
    rng = np.random.default_rng(20261120)
    wl = np.arange(350.0, 801.0)
    cases = []
    for i in range(20):
        centers = rng.uniform(405., 705., 3)
        widths = rng.uniform(35., 150., 3)
        amplitudes = rng.uniform(0.0003, 0.0045, 3)
        r = np.full(wl.shape, rng.uniform(0.0002, 0.0015))
        for center, width, amplitude in zip(centers, widths, amplitudes):
            r += amplitude * np.exp(-((wl - center) / width) ** 2)
        g0 = (rng.uniform(0., 87.5), rng.uniform(0., 87.5), rng.uniform(0., 180.))
        g1 = (rng.uniform(0., 87.5), rng.uniform(0., 87.5), rng.uniform(0., 180.))
        cases.append(Case(f"random-{i:02d}", wl, r, g0, g1))
    return cases


CASES = _deterministic_cases() + _edge_cases() + _random_cases()


@pytest.fixture(scope="module")
def model() -> O25Model:
    return O25Model()


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.case_id)
def test_new_class_core_matches_old_procedural_core(case: Case, model: O25Model):
    old = procedural_o25(case.wl.copy(), case.Rrs.copy(), np.array(case.g0), np.array(case.g1))
    new = model._correct_o25(case.wl.copy(), case.Rrs.copy(), np.array(case.g0), np.array(case.g1))
    for name, expected, actual in zip(("a", "bb", "Rrs"), old, new):
        np.testing.assert_allclose(
            actual, expected, rtol=2e-14, atol=2e-15,
            err_msg=f"{case.case_id}: {name}",
        )


@pytest.mark.parametrize("case", _edge_cases()[:2], ids=lambda case: case.case_id)
def test_identity_correction_returns_input_spectrum(case: Case, model: O25Model):
    _, _, corrected = model._correct_o25(case.wl, case.Rrs, np.array(case.g0), np.array(case.g1))
    np.testing.assert_allclose(corrected, case.Rrs, rtol=2e-14, atol=2e-15)


def test_all_user_interfaces_share_the_new_class_core():
    wl = np.array([443., 490., 560., 665.])
    rrs = _shape(wl, "green")
    g0, g1 = (30., 20., 120.), (40., 10., 75.)
    direct = O25Model()._correct_o25(wl, rrs, np.array(g0), np.array(g1))
    model_result = O25Model().correct(wl, rrs, g0, g1)
    public_result = o25.correct(wl, rrs, g0, g1)
    compatibility = o25.O25_hyp(wl, rrs, g0, g1)
    for expected, via_model, via_public, via_compatibility in zip(
        direct,
        (model_result.a, model_result.bb, model_result.Rrs),
        (public_result.a, public_result.bb, public_result.Rrs),
        compatibility,
    ):
        np.testing.assert_array_equal(via_model, expected)
        np.testing.assert_array_equal(via_public, expected)
        np.testing.assert_array_equal(via_compatibility, expected)
