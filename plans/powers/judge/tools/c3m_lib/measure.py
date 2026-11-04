"""Measurement layer: feats become dimensionless ratios to reference objects that
exist in both universes, then tiers (log10 joules in our universe's units)."""
from __future__ import annotations
from dataclasses import dataclass
from functools import total_ordering
import numpy as np

# Reference energies in our universe (joules)
REFERENCE_J = {
    "human_punch": 1e3,
    "granite_frag_per_cc": 8.0,        # J/cm^3, fragmentation (conventional calc value)
    "tnt_ton": 4.184e9,
    "moon_gbe": 1.24e29,               # gravitational binding energy
    "earth_gbe": 2.24e32,
    "sun_luminosity_per_s": 3.828e26,
}


def tier(E_joules):
    return np.log10(E_joules)


def tier_from_ratio(pi, reference):
    """Universe-invariant: tier = log10(pi * E_R in our universe)."""
    return np.log10(pi) + np.log10(REFERENCE_J[reference])


def sphere_frag_tier(diameter_m, j_per_cc=REFERENCE_J["granite_frag_per_cc"]):
    vol_cc = (4 / 3) * np.pi * (diameter_m / 2) ** 3 * 1e6
    return tier(vol_cc * j_per_cc)


def uniform_sphere_gbe(mass_kg, radius_m, G=6.674e-11):
    return 3 * G * mass_kg ** 2 / (5 * radius_m)


@total_ordering
@dataclass(frozen=True)
class Level:
    """Lexicographic level: (infinite class, finite tier). Class 0 = finite.
    Class c >= 1 = a demonstrated infinity of cardinality rank c (aleph_{c-1}).
    Any infinite class outranks every finite tier; unverified claims stay class 0."""
    cls: int
    t: float = 0.0

    def __lt__(self, other):
        return (self.cls, self.t if self.cls == 0 else 0.0) < (other.cls, other.t if other.cls == 0 else 0.0)

    def __eq__(self, other):
        return (self.cls, self.t if self.cls == 0 else 0.0) == (other.cls, other.t if other.cls == 0 else 0.0)

    def __hash__(self):
        return hash((self.cls, self.t if self.cls == 0 else 0.0))
