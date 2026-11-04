"""Inference layer: hierarchical robust (Student-t) model for latent capability.

    x_ij | theta_i  ~  t_nu( theta_i + b_ij ,  s_ij^2 / w_ij )
    theta_i | mu_U  ~  N( mu_U , tau^2 )
    mu_U            ~  N( m0 , s0^2 )

b_ij is a known source-type offset whose own uncertainty is folded into s_ij.
Sampled exactly by Gibbs using the scale-mixture form of the t distribution:
x_ij ~ N(theta_i + b_ij, s_ij^2 / (w_ij * lam_ij)), lam_ij ~ Gamma(nu/2, nu/2).
"""
from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np

SOURCE_BIAS = {  # (offset in tiers, extra sd) by source type; positive = inflates
    "primary": (0.0, 0.0),
    "author": (0.0, 0.2),
    "anime": (0.3, 0.3),
    "game": (0.5, 0.5),
    "scaled": (0.0, 0.0),  # scaling-chain variance comes from the network layer
}


@dataclass
class Feat:
    x: float          # measured value (tier or log10 m/s)
    sd: float         # calculation uncertainty
    w: float = 1.0    # canon reliability weight in (0, 1]
    source: str = "primary"
    note: str = ""

    def effective(self):
        b, extra = SOURCE_BIAS[self.source]
        return self.x, b, np.sqrt(self.sd ** 2 + extra ** 2)


@dataclass
class Character:
    name: str
    universe: str
    feats: list = field(default_factory=list)


def gibbs(chars, nu=4.0, tau=3.0, m0=0.0, s0=20.0, n_iter=6000, burn=1000,
          chains=4, seed=0):
    """Returns dict name -> array (chains, draws) of theta, and mu per universe."""
    rng = np.random.default_rng(seed)
    unis = sorted({c.universe for c in chars})
    uidx = {u: i for i, u in enumerate(unis)}
    data = []
    for c in chars:
        x, b, s = map(np.array, zip(*[f.effective() for f in c.feats]))
        w = np.array([f.w for f in c.feats])
        data.append((x, b, s ** 2 / w))
    C = len(chars)
    out = np.empty((chains, n_iter - burn, C))
    mu_out = np.empty((chains, n_iter - burn, len(unis)))
    for ch in range(chains):
        theta = np.array([np.median(x - b) for x, b, _ in data]) + rng.normal(0, 1, C)
        mu = np.zeros(len(unis))
        lam = [np.ones_like(x) for x, _, _ in data]
        for it in range(n_iter):
            for i, (x, b, v) in enumerate(data):
                r = x - b - theta[i]
                lam[i] = rng.gamma((nu + 1) / 2, 2.0 / (nu + r ** 2 / v))
                prec = np.sum(lam[i] / v) + 1 / tau ** 2
                mean = (np.sum(lam[i] * (x - b) / v) + mu[uidx[chars[i].universe]] / tau ** 2) / prec
                theta[i] = rng.normal(mean, 1 / np.sqrt(prec))
            for u, j in uidx.items():
                th = np.array([theta[i] for i in range(C) if chars[i].universe == u])
                prec = len(th) / tau ** 2 + 1 / s0 ** 2
                mean = (th.sum() / tau ** 2 + m0 / s0 ** 2) / prec
                mu[j] = rng.normal(mean, 1 / np.sqrt(prec))
            if it >= burn:
                out[ch, it - burn] = theta
                mu_out[ch, it - burn] = mu
    return {c.name: out[:, :, i] for i, c in enumerate(chars)}, {u: mu_out[:, :, j] for u, j in uidx.items()}


def split_rhat(draws):
    """Split-R-hat (Gelman et al. 2013) for array (chains, n)."""
    c, n = draws.shape
    h = n // 2
    x = np.concatenate([draws[:, :h], draws[:, h:2 * h]], axis=0)
    m, n = x.shape
    W = x.var(axis=1, ddof=1).mean()
    B = n * x.mean(axis=1).var(ddof=1)
    var = (n - 1) / n * W + B / n
    return float(np.sqrt(var / W))


def ess(draws):
    """Bulk effective sample size via initial positive sequence of autocorrelations."""
    c, n = draws.shape
    x = draws - draws.mean(axis=1, keepdims=True)
    f = np.fft.rfft(x, 2 * n, axis=1)
    ac = np.fft.irfft(f * np.conj(f), axis=1)[:, :n].mean(axis=0)
    ac /= ac[0]
    s, t = 0.0, 1
    while t + 1 < n:
        pair = ac[t] + ac[t + 1]
        if pair < 0:
            break
        s += pair; t += 2
    return float(c * n / (1 + 2 * s))


def ppp_max(theta_draws, feats, nu=4.0, rng=None):
    """Posterior predictive p-value of the largest feat: P(max replicated >= max observed).
    Small values flag the top feat as an outlier relative to the model."""
    rng = np.random.default_rng(rng)
    th = theta_draws.ravel()
    x, b, s = map(np.array, zip(*[f.effective() for f in feats]))
    w = np.array([f.w for f in feats]); sc = s / np.sqrt(w)
    rep = th[:, None] + b + sc * rng.standard_t(nu, size=(th.size, x.size))
    return float(np.mean(rep.max(axis=1) >= x.max()))
