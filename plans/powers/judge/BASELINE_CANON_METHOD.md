# Baseline: method error and canon weights (REFINABLE BASELINE, 11-05)
Replaces the guessed METHOD_SD .2/.3/.4/.6 and CANON_W 1/.5/.5/.2. Derived from the c3m code (c3m.zip: inference.py, measure.py, combat.py) and checked with `tools/baseline_check.py`. Wired into `tools/feats.py`. Refit when real feats exist (see "How to refine").

## 1. Validator math: verified
- measure.py/inference.py copies in tools/c3m_lib are the c3m ones. Tier = log10 joules (AP, Dur) or log10 m/s (v).
- Constants reproduce c3m's own references: uniform-sphere binding energy of Earth gives 32.3506 vs log10(earth_gbe 2.24e32) = 32.3502; Moon 29.094 vs 29.093; 1 megaton TNT 15.6216 exact; c = 8.4768; 1 m granite sphere at 8 J/cm3 = 6.622 (= plain recomputation).
- inference.py: x ~ t4(theta + b, s^2/w). So `sd` is the calculation sd in tiers and `w` divides the variance (w=.5 means sd x 1.41). SOURCE_BIAS shifts game +0.5 tier and adds sd .5 (so game feats are already penalised).
- combat.py (win probability from AP, Dur, v) does not use sd or w. It consumes the posterior of theta, so these values only matter through the width of each posterior.
- Weakness seen: validate.py accepts a feat if the plain recomputation matches T OR T minus off. T never contains the bias (bias is applied in the model), so the second branch is unneeded. Harmless, left alone.
- combat.py not used by judging; judges never compute tiers.

## 2. Method sd (calculation error, tiers = dex)
Old rule: one flat sd per method, the max over inputs. That ignores that a cube (sphere diameter) multiplies input error by 3 while a stated energy multiplies it by 1. New rule, per feat:

`sd = sqrt( FLOOR[template]^2 + sum_inputs (EXP[template][input] x INPUT_SD[method])^2 )`

INPUT_SD (1 sd of log10 of the input):
| method | dex | why |
|---|---|---|
| stated | .05 | printed number: Benford rounding error is .082 dex at 1 significant figure, .008 at 2; typical pages mix both, plus unit slips |
| measured | .08 | size read off the same scene, about 20% (log10 1.2) |
| scaled | .20 | real-world reference object, about 60% spread (log10 1.6) |
| estimated | .40 | factor 2.5 guess |

EXP = the power of the input in the formula (kinetic: mass 1, speed 2; fragment_sphere: diameter 3; uniform_sphere_gbe: mass 2, radius 1; others 1).
FLOOR = template and convention error: stated_energy/stated_speed .05; kinetic, luminous, travel .10 (efficiency, average vs peak); uniform_sphere_gbe .15 (density profile); vaporize .20; fragment_sphere/volume .30 (J/cm3 convention spans a wide range).

Resulting sd:
| feat | old | new |
|---|---|---|
| stated energy | .2 | .07 |
| kinetic, mass stated, speed measured | .3 | .20 |
| 10 m sphere, measured, J/cm3 scaled | .4 | .43 |
| 1 km sphere, scaled | .4 | .70 |
| 1 km sphere, estimated | .6 | 1.25 |
A printed number is much tighter than the guess; anything cubed from a reference object or a guess is much looser. That is the correct direction: judges are not penalised for stated feats, and guessed sizes cannot dominate.

## 3. Canon weights
w = s0^2 / (s0^2 + sc^2), s0 = .3 (typical calc sd), sc = extra scatter of that canon around main canon:
| canon | sc | w |
|---|---|---|
| main | 0 | 1.0 |
| extended (movies, spin-offs, novelisations) | .3 | .5 |
| noncanon (fanon, what-ifs, debates) | .6 | .2 |
| games | n/a | 1.0 |
Games went .5 -> 1.0: game wikis get `st=game` (judge.py sets it from GAME), and SOURCE_BIAS already adds +.5 tier and sd .5. A further .5 weight double counted. If a games-canon feat arrives with a non-game st, treat it as extended (.5) by hand.

## 4. Test
`python3 -I tools/baseline_check.py` runs the real c3m Gibbs model (Student-t, tau 3) on sample characters, 90% posterior width in tiers, new vs old:
- one stated 1e15 J, main: .30 vs .86; three agreeing: .13 vs .37
- one stated, game wiki: 2.16 vs 4.34 (median 14.5, bias applied)
- one scaled 1 km sphere: 2.99 vs 1.71; estimated: 5.26 vs 2.56 (cubed guesses are now honestly wide)
- stated 1e15 main + 1e18 noncanon: median 15.03 vs 15.12, the noncanon outlier barely moves it
Passing shards 160, 161, 162, 167, 177 hold zero feats (the game damage numbers are correctly left out), so there are no real shard feats to test; the check uses realistic templates instead. The change does not alter any existing shard output.

## How to refine
1. After the first judged shards with feats land, collect feats of one entity from several pages and compare scatter by method; set INPUT_SD to the measured sd, and sc per canon from the same.
2. Re-run baseline_check.py, update the tables, keep this file as the reasoning record.
3. Marlon's own numbers override any value here.
