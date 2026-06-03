#!/usr/bin/env python3 -B
"""sd.py v2: tiny system dynamics for SE.

Conventions
-----------
* Var names: UPPER = input (state of world), lower = param (process IS).
* Bundle: namedtuple Model(init, step, y, rq, ctrl).
  - init  : {'k': [default, lo, hi]}     (UPPER and lower mixed)
  - step  : (dt, t, u, v) -> None
  - y     : list[(t,row)] -> float       (higher = better)
  - rq    : (bg=None) -> dict {verdict, y0, y1, gap, desc}
  - ctrl  : str, name of the var rq() flips (frozen during stress(target='params'))

Engine
------
run(init, step, dt=1, tmax=20, mode='clip')
  mode='clip'   : clamp states at [lo,hi] each step (default)
  mode='reject' : return None if any state escapes [lo,hi] (anti-cheat)

Stress
------
stress(model_factory, target='inputs'|'params'|'all', n=500, seed=1)
  Background-perturbation harness. ctrl variable is never perturbed.

Optimizer
---------
opt(model_factory, narrow=0.6, ...)
  narrow=1.0 -> sample full [lo,hi]; narrow=0.6 -> shrink to centered 60%.
  narrow<1 prevents the optimizer from "winning" via near-boundary starts.

Refs (see evidence.md for parameter justifications and quotes):
[1]  Brooks (1975)               [9]  Becker et al. METR (2025)
[2]  Goel & Okumoto (1979)        [10] GitHub Engineering RCT (2024)
[3]  Cunningham (1992)            [11] Luo et al. flaky tests (2014)
[4]  Kermack & McKendrick (1927)  [12] Forsgren, Humble, Kim (2018)
[5]  Abdel-Hamid & Madnick (1991) [13] Skelton & Pais (2019)
[6]  Sterman (2000)               [14] Newman (2015)
[7]  Madachy (2008)               [15] DORA wellbeing (2024)
[8]  Harding GitClear (2024)
"""

import math, random
from collections import namedtuple

Model = namedtuple('Model', 'init step y rq ctrl')

class S:
  """Lightweight attribute bag (replaces SimpleNamespace)."""
  def __init__(self, **kw):
    for k, val in kw.items(): setattr(self, k, val)

def make_state(d):
  s = S()
  for k, val in d.items(): setattr(s, k, val)
  return s

# --- Engine -----------------------------------------------------------------

def run(init, step, dt=1, tmax=20, mode='clip'):
  """Simulate. mode='clip' clamps; mode='reject' returns None on escape.
  init values are [default, lo, hi] OR [default, lo, hi, 'unit'] —
  the optional 4th element is human-readable documentation, ignored
  by the engine."""
  u = make_state({k: v[0] for k, v in init.items()})
  out, t = [], 0
  while t < tmax:
    v = make_state(vars(u))
    step(dt, t, u, v)
    for k, spec in init.items():
      lo, hi = spec[1], spec[2]            # tolerate [d,lo,hi] or [d,lo,hi,unit]
      val = getattr(v, k)
      if mode == 'reject' and (val < lo - 1e-9 or val > hi + 1e-9):
        return None
      setattr(v, k, max(lo, min(hi, val)))
    out.append((t, v))
    u = v
    t += dt
  return out

# --- Verdict helpers --------------------------------------------------------

def verdict(desc, y0, y1, expect='down'):
  """Single-shot verdict. Compares one y0 vs one y1 with a 5%-of-y0
  heuristic threshold (floor 0.5). Kept for backward compat; the
  stats-grade replacement is verdict_n() below."""
  signed = (y0 - y1) if expect == 'down' else (y1 - y0)
  thresh = max(abs(y0) * 0.05, 0.5)
  v = ('CONFIRM' if signed >  thresh else
       'REFUTE'  if signed < -thresh else 'neutral')
  return {'verdict': v, 'y0': y0, 'y1': y1, 'gap': y1 - y0, 'desc': desc}


def verdict_n(desc, y0s, y1s, expect='down'):
  """N-shot verdict using stats.same (Cliff's delta + KS + median-eps).
  y0s, y1s = lists of y values (one per perturbed run).
  Returns CONFIRM / REFUTE / neutral plus pooled diagnostics.
  Same: lists statistically indistinguishable -> neutral.
  Different: direction by median difference -> CONFIRM / REFUTE."""
  import stats as st
  n0 = st.adds(y0s); n1 = st.adds(y1s)
  eps = st.spread(n0) * st.the.stats.eps      # 0.35 * sd(y0s)
  if st.same(y0s, y1s, eps):
    v = 'neutral'
  else:
    signed = (n0.mu - n1.mu) if expect == 'down' else (n1.mu - n0.mu)
    v = 'CONFIRM' if signed > 0 else 'REFUTE'
  return {'verdict': v, 'y0': n0.mu, 'y1': n1.mu,
          'gap': n1.mu - n0.mu, 'desc': desc,
          'sd0': n0.sd, 'sd1': n1.sd, 'eps': eps,
          'n': len(y0s)}

# --- Distribution sampler --------------------------------------------------

def sample(rng, default, lo, hi, dist='triangular'):
  """Draw one value from [lo, hi]. dist='triangular' peaks at default
  (author's prior); dist='uniform' is equal weight across [lo, hi]
  (adversarial sweep). Degenerate edges (default==lo or default==hi)
  collapse the triangular into a half-triangle automatically."""
  if dist == 'uniform':
    return rng.uniform(lo, hi)
  if dist == 'triangular':
    # random.triangular(low, high, mode); requires lo <= default <= hi
    mode = max(lo, min(hi, default))
    return rng.triangular(lo, hi, mode)
  raise ValueError(f"unknown dist: {dist}")


# --- Optimizer (with narrow search to prevent boundary-cheating) ------------

def opt(model_factory, init=None, n=1000, seed=1, dt=1, tmax=20, narrow=0.6,
        dist='triangular'):
  """Sample n random starts. narrow shrinks the sample range to a centered
  fraction of [lo,hi] (e.g. narrow=0.6 -> middle 60%). dist picks the
  sampler ('triangular' peaks at default; 'uniform' equal weight).
  Returns dict(init=tightened_ranges, best=(score, params), top=[...])."""
  m = model_factory()
  init0 = m.init if init is None else init
  rng = random.Random(seed)
  rows = []
  for _ in range(n):
    init1 = {}
    for k, spec in init0.items():
      default, lo, hi = spec[0], spec[1], spec[2]
      mid = (lo + hi) / 2
      half = (hi - lo) / 2 * narrow
      lo_n = max(lo, mid - half)
      hi_n = min(hi, mid + half)
      init1[k] = [sample(rng, default, lo_n, hi_n, dist), lo, hi]
    out = run(init1, m.step, dt, tmax)
    rows.append((m.y(out), {k: init1[k][0] for k in init1}))
  rows.sort(key=lambda r: -r[0])
  top = rows[: max(2, int(n**0.5))]
  new = {}
  for k in init0:
    vs = sorted(r[1][k] for r in top)
    new[k] = [vs[len(vs)//2], vs[0], vs[-1]]
  return {'init': new, 'best': top[0], 'top': top}

# --- Unified stress: target = inputs | params | all -------------------------

def stress(model_factory, target='all', n=500, seed=1, dist='triangular'):
  """Sample n random backgrounds. target picks which vars to perturb:
    'inputs' : UPPER-cased only
    'params' : lower-cased only (excludes ctrl)
    'all'    : everything except ctrl
  dist='triangular' (default) weights samples near the author's
  declared default; dist='uniform' is adversarial equal-weight across
  [lo, hi]. Returns dict(counts={CONFIRM/REFUTE/neutral counts},
  refuters=[...])."""
  m = model_factory()
  rng = random.Random(seed)
  counts = {'CONFIRM': 0, 'REFUTE': 0, 'neutral': 0}
  refuters = []

  def perturb(k):
    if k == m.ctrl: return False
    if target == 'inputs':  return k[0].isupper()
    if target == 'params':  return k[0].islower()
    if target == 'all':     return True
    raise ValueError(target)

  for _ in range(n):
    bg = {k: list(v) for k, v in m.init.items()}
    for k, spec in m.init.items():
      default, lo, hi = spec[0], spec[1], spec[2]
      if perturb(k):
        bg[k] = [sample(rng, default, lo, hi, dist), lo, hi]
    r = m.rq(bg)
    counts[r['verdict']] += 1
    if r['verdict'] == 'REFUTE':
      refuters.append((bg, r))
  return {'counts': counts, 'refuters': refuters}


# --- Stats-grade verdict (N-shot, perturbed) --------------------------------

def _infer_expect(m):
  """Derive a model's hypothesis direction from one default rq() call.
  CONFIRM with gap<0 -> expect='down'. CONFIRM with gap>0 -> 'up'.
  REFUTE flips. neutral falls back to the sign of the gap that would
  have been CONFIRM under either direction (default 'down')."""
  r = m.rq()
  v, gap = r['verdict'], r['gap']
  if v == 'CONFIRM':  return 'down' if gap < 0 else 'up'
  if v == 'REFUTE':   return 'down' if gap > 0 else 'up'
  return 'down'


def rq_n(model_factory, n=100, seed=1, dist='triangular', target='all'):
  """Run model.rq() n times with perturbed background, collect the
  resulting y0 / y1 lists, classify via verdict_n (stats.same).
  Recommended replacement for single-shot rq(). target picks which vars
  to perturb (same semantics as stress)."""
  m = model_factory()
  expect = _infer_expect(m)
  rng = random.Random(seed)

  def should_perturb(k):
    if k == m.ctrl: return False
    if target == 'inputs':  return k[0].isupper()
    if target == 'params':  return k[0].islower()
    if target == 'all':     return True
    raise ValueError(target)

  y0s, y1s, last = [], [], None
  for _ in range(n):
    bg = {k: list(v) for k, v in m.init.items()}
    for k, spec in m.init.items():
      default, lo, hi = spec[0], spec[1], spec[2]
      if should_perturb(k):
        bg[k] = [sample(rng, default, lo, hi, dist), lo, hi]
    r = m.rq(bg=bg)
    y0s.append(r['y0']); y1s.append(r['y1']); last = r
  return verdict_n(last['desc'], y0s, y1s, expect=expect)


# --- Models -----------------------------------------------------------------
# Naming: UPPER = input (world state), lower = param (process configuration).
# Hidden rate constants from v1 are now lifted into init as lowercase params.

def diapers():
  """Toy: weekly diaper supply.  Sat = bulk buy + wash all dirty.
  RQ: skip wash on Sat t=13 -> dirty pileup."""
  init = {'Clean':[100,0,200,'diapers'], 'Dirty':[0,0,200,'diapers'], 'Buy':[0,0,100,'diapers/tick'],
          'Use':[8,0,20,'diapers/tick'], 'wash_amt':[0,0,200,'diapers/tick'], 'skip':[0,0,1,'frac']}

  def step(dt, t, u, v):
    sat = int(t) % 7 == 6
    v.Clean = u.Clean + dt * (u.Buy - u.Use)
    v.Dirty = v.Dirty + dt * (u.Use - u.wash_amt)
    v.Buy   = 70 if sat else 0
    v.wash_amt = u.Dirty if sat else 0
    if t == 13 and u.skip > 0.5: v.wash_amt = 0
    v.skip = u.skip

  def y(out):
    return min(r.Clean for _, r in out) - 0.5 * max(r.Dirty for _, r in out)

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("skip wash@t=13 -> Dirty pileup",
                   y(run({**bi, 'skip':[0,0,1,'frac']}, step)),
                   y(run({**bi, 'skip':[1,0,1,'frac']}, step)), 'down')

  return Model(init, step, y, rq, 'skip')


def brooks():
  """Brooks [1] Mythical Man-Month: adding people to a late project
  makes it later. Two compounding effects: (1) quadratic communication
  overhead n*(n-1)/2 grows fast as team size grows; (2) each newcomer
  drains a fraction of veteran capacity for training until they mature.

  Stocks: Vet, New, Todo, Done. Done is the success measure.
  Control: boost (size of mid-project late-hire shock).
  RQ: a boost=10 cohort at t=10 reduces net progress vs boost=0.
  Hypothesis basis: comm + train terms together can swamp prod_rate when
  Vet is already busy; the model expresses Brooks's claim mechanistically."""
  init = {'Vet':[10,0,100,'devs'], 'New':[0,0,100,'devs'],
          'Done':[0,0,500,'items'], 'Todo':[500,0,500,'items'],
          # ctrl: late-hire shock size injected at t=10
          'boost':[0,0,100,'devs'],
          # Communication coefficient per dev-pair (Brooks: 0.005 = 0.5% drag/pair)
          'comm_coef':[0.005,0,0.05,'frac/pair'],
          # Training drag per newcomer on veteran capacity
          'train_coef':[0.2,0,1,'frac/newhire'],
          'prod_rate':[5,0.1,20,'items/vet/tick'],
          # New -> Vet maturation rate (per-tick fraction of New cohort)
          'mature_rate':[0.1,0,1,'frac/tick']}

  def step(dt, t, u, v):
    # Quadratic communication overhead: n*(n-1)/2 pairs * per-pair drag.
    # This is the term Brooks called out: linear growth in headcount
    # gives quadratic growth in coordination cost.
    comm  = u.Vet * (u.Vet - 1) / 2 * u.comm_coef
    # Training drag: each newcomer takes a fraction of veteran time.
    train = u.New * u.train_coef
    # Effective productivity = veterans * remaining capacity * base rate.
    prod  = u.Vet * (1 - comm - train) * u.prod_rate
    # max(0, prod) clamps: comm + train can exceed 1.0 with large teams,
    # which would otherwise produce NEGATIVE Done. The clamp is the model
    # expressing "team produces nothing" rather than "team un-produces."
    v.Todo = u.Todo - dt * max(0, prod)
    v.Done = u.Done + dt * max(0, prod)
    # New decays into Vet at mature_rate; boost injects at t=10 only.
    v.New  = u.New - dt * u.mature_rate * u.New + (u.boost if t == 10 else 0)
    v.Vet  = u.Vet + dt * u.mature_rate * u.New
    for p in ('boost','comm_coef','train_coef','prod_rate','mature_rate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Success = net progress (Done - remaining Todo). Penalises slack.
    end = out[-1][1]
    return end.Done - end.Todo

  def rq(bg=None):
    # Two-arm: boost=0 (no late hire) vs boost=10 (10 newcomers at t=10).
    # 'down' expected: the boost increases comm + train drag faster than
    # the eventual maturation of the newcomers can pay back.
    bi = init if bg is None else bg
    return verdict("boost=10 hurts net progress",
                   y(run({**bi, 'boost':[0,0,100,'devs']}, step)),
                   y(run({**bi, 'boost':[10,0,100,'devs']}, step)), 'down')

  return Model(init, step, y, rq, 'boost')


def bugs():
  """Goel-Okumoto [2]: classical software reliability growth model.
  An unknown pool of latent defects is discovered at a rate proportional
  to the remaining latent stock — yielding the canonical exponential
  N(t) = a*(1 - e^(-bt)). Found bugs then feed a fix pipeline.

  Stocks: Latent -> Found -> Fixed. Fixed is the success measure.
  Control: Latent (initial pool size — the model's input distribution).
  RQ: doubling Latent at t=0 doubles mid-curve Fixed (linearity probe).
  Hypothesis basis: the integral is linear in Latent by construction,
  so the test catches the linearity — exactly the model's reason to exist."""
  init = {'Latent':[100,0,200,'bugs'], 'Found':[0,0,200,'bugs'],
          'Fixed':[0,0,200,'bugs'],
          # Discovery rate (Goel-Okumoto 'b' parameter): fraction of
          # Latent found per tick.
          'find_rate':[0.15,0.01,0.5,'frac/tick'],
          # Fix rate: fraction of Found resolved per tick.
          'fix_rate':[0.5,0.05,1,'frac/tick']}

  def step(dt, t, u, v):
    # Two coupled exponentials: each rate consumes its source stock at
    # a fixed per-tick fraction.
    find = u.Latent * u.find_rate
    fix  = u.Found  * u.fix_rate
    v.Latent = u.Latent - dt * find
    v.Found  = u.Found  + dt * (find - fix)
    v.Fixed  = u.Fixed  + dt * fix
    v.find_rate, v.fix_rate = u.find_rate, u.fix_rate

  def y(out):
    """Mid-curve recovery (t=10 of 20): tests scaling, not asymptote.
    Asymptote is always ~1.0 by construction (exponential decay)."""
    mid_idx = len(out) // 2
    return out[mid_idx][1].Fixed

  def rq(bg=None):
    # Doubling initial Latent: y should scale linearly. 'up' = treated
    # arm (Latent=100) HIGHER than baseline (Latent=50). The PASS here
    # IS the linearity claim — see mr_scale interaction in tests.py.
    bi = init if bg is None else bg
    return verdict("2x initial Latent -> ~2x mid-curve Fixed",
                   y(run({**bi, 'Latent':[50,0,200,'bugs']}, step)),
                   y(run({**bi, 'Latent':[100,0,200,'bugs']}, step)), 'up')

  return Model(init, step, y, rq, 'Latent')


def debt():
  """Cunningham [3] technical-debt metaphor: shipping fast incurs debt;
  debt slows future shipping; debt compounds (intr_rate) until paid down.

  Stocks: Feat (shipped features), Debt (accumulated debt), Vel
  (instantaneous velocity readout). y combines high Feat with low Debt.
  Control: starting Debt level (the legacy-codebase scenario).
  RQ: starting Debt=50 reduces net delivery vs starting Debt=0.
  Hypothesis basis: speed = 1 - Debt/100 creates a debt-velocity
  feedback loop; whether Debt dominates depends on pay_rate vs
  (born_rate + intr_rate)."""
  init = {'Feat':[1,0,200,'items'], 'Debt':[0,0,100,'debt-items'],
          'Vel':[10,0,20,'items/tick'],
          # Debt accrual per item shipped (born_rate * ship)
          'born_rate':[0.3,0,1,'debt/tick'],
          # Compound interest on outstanding debt
          'intr_rate':[0.10,0,0.5,'frac/tick'],
          # Debt repayment rate (refactoring share of effort)
          'pay_rate':[0.15,0,1,'frac/tick']}

  def step(dt, t, u, v):
    # Velocity choked by debt linearly; floor at 0 to avoid negative ship.
    speed = max(0, 1 - u.Debt / 100)
    # ship grows with feature stock (1 + Feat*0.1 = compound benefit
    # of past delivery) but is gated by current speed.
    ship  = (1 + u.Feat * 0.1) * speed
    born  = ship * u.born_rate           # new debt per unit shipped
    intr  = u.Debt * u.intr_rate         # compound interest
    pay   = u.Debt * u.pay_rate          # refactoring repayment
    v.Feat = u.Feat + dt * ship
    v.Debt = u.Debt + dt * (born + intr - pay)
    v.Vel  = 10 * speed
    v.born_rate, v.intr_rate, v.pay_rate = u.born_rate, u.intr_rate, u.pay_rate

  def y(out):
    # Trade-off measure: end-state features minus mean Debt over the run.
    # Mean (not end) Debt penalises trajectories that pile up debt early.
    end = out[-1][1]
    md = sum(r.Debt for _, r in out) / len(out)
    return end.Feat - md

  def rq(bg=None):
    # 'down' = treated (Debt=50) WORSE than baseline (Debt=0).
    # The hypothesis is the legacy-codebase penalty.
    bi = init if bg is None else bg
    return verdict("starting Debt=50 slows delivery",
                   y(run({**bi, 'Debt':[0,0,100,'debt-items']}, step)),
                   y(run({**bi, 'Debt':[50,0,100,'debt-items']}, step)), 'down')

  return Model(init, step, y, rq, 'Debt')


def sir():
  """Kermack-McKendrick [4] SIR model applied to bad-pattern spread.
  Each module is Susceptible, Infected (carries the anti-pattern), or
  Recovered (refactored, immune). Infection spreads on contact;
  recovery happens at a fixed rate.

  Stocks: S, I, R (sum conserved). y = -max(I) — peak epidemic size
  (negated so that LOWER peak = HIGHER y, matching the down-good convention).
  Control: I (initial infected count — the seed-bug-count scenario).
  RQ: tripling I raises peak; y becomes more negative.
  Hypothesis basis: standard SIR has a quadratic infection term
  beta*S*I so initial-condition variation propagates supra-linearly."""
  init = {'S':[90,0,100,'modules'], 'I':[10,0,100,'modules'],
          'R':[0,0,100,'modules'],
          # Per-contact transmission probability (Kermack: 0.0051 chosen
          # so R0 ≈ 3 at the default scale — moderate outbreak regime)
          'beta':[0.0051,0,0.05,'frac/contact'],
          # Per-tick recovery probability (refactoring rate)
          'gamma':[0.15,0,1,'frac/tick']}

  def step(dt, t, u, v):
    inf = u.beta  * u.S * u.I   # mass-action infection (quadratic in S,I)
    rec = u.gamma * u.I
    v.S = u.S - dt * inf
    v.I = u.I + dt * (inf - rec)
    v.R = u.R + dt * rec
    v.beta, v.gamma = u.beta, u.gamma

  def y(out):
    # Peak Infected is the policy-relevant metric (hospitalisation,
    # in the public-health analogue). Negate so the down-good convention
    # holds: lower peak = better outcome = higher y.
    return -max(r.I for _, r in out)

  def rq(bg=None):
    # 'down' = treated (I=30) WORSE (i.e. y more negative due to higher
    # peak). Tests the SIR nonlinearity sensitivity to initial conditions.
    bi = init if bg is None else bg
    return verdict("3x initial I raises peak",
                   y(run({**bi, 'I':[10,0,100,'modules']}, step)),
                   y(run({**bi, 'I':[30,0,100,'modules']}, step)), 'down')

  return Model(init, step, y, rq, 'I')


def rework():
  """Abdel-Hamid & Madnick [5] hidden rework cycle: failed test items
  flow back to Rew, where fixes feed back into Dev. The cycle is "hidden"
  because it inflates Dev volume invisibly to the requirements pipeline.

  Stocks: Req -> Dev -> Test -> {Done, Rew} -> Dev. Done is the goal;
  WIP (Dev + Test + Rew) is the cost.
  Control: failrate (probability a Test item fails and gets reworked).
  RQ: failrate 0.7 collapses net Done by feeding too much back through Rew.
  Hypothesis basis: at high failrate, the Test -> Rew -> Dev loop
  dominates the Test -> Done flow, eventually starving Done growth."""
  init = {'Req':[100,0,100,'items'], 'Dev':[0,0,100,'items'],
          'Test':[0,0,100,'items'], 'Rew':[0,0,100,'items'],
          'Done':[0,0,100,'items'],
          'code_rate':[0.2,0,1,'frac/tick'],
          'qa_rate':[0.5,0,1,'frac/tick'],
          'fix_rate':[0.5,0,1,'frac/tick'],
          # ctrl: share of Test items that fail (and feed Rew)
          'failrate':[0.4,0,1,'frac']}

  def step(dt, t, u, v):
    code = u.Req  * u.code_rate
    qa   = u.Dev  * u.qa_rate
    # Split Test outflow: fail goes to Rew (hidden loop), pas goes to Done.
    fail = u.Test * u.failrate
    pas  = u.Test * (1 - u.failrate)
    fix  = u.Rew  * u.fix_rate            # Rew -> Dev (rework returns)
    v.Req  = u.Req  - dt * code
    # Dev gains both new code AND fixed rework — the hidden inflow.
    v.Dev  = u.Dev  + dt * (code - qa + fix)
    v.Test = u.Test + dt * (qa - fail - pas)
    v.Rew  = u.Rew  + dt * (fail - fix)
    v.Done = u.Done + dt * pas
    for p in ('code_rate','qa_rate','fix_rate','failrate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Reward Done, penalise mean WIP (the cost of carrying half-done work).
    # 0.5x weight matches "WIP is half as bad as not-Done".
    end = out[-1][1].Done
    wip = sum(r.Dev + r.Test + r.Rew for _, r in out) / len(out)
    return end - 0.5 * wip

  def rq(bg=None):
    # 'down' = failrate=0.7 collapses y vs failrate=0.1 (the rework
    # loop runs away).
    bi = init if bg is None else bg
    return verdict("failrate 0.7 -> hidden rework dominates",
                   y(run({**bi, 'failrate':[0.1,0,1,'frac']}, step)),
                   y(run({**bi, 'failrate':[0.7,0,1,'frac']}, step)), 'down')

  return Model(init, step, y, rq, 'failrate')


def learn():
  """Sterman [6] workforce-pipeline model. Jr (junior) -> Tr (trainee) ->
  Sr (senior). Seniors mentor incoming Jr cohorts; the loop depends on
  having seniors AT ALL to seed the next generation.

  Stocks: Jr, Tr, Sr, Ment (cumulative mentor-time delivered).
  Control: Sr (initial senior count — the pipeline-seed scenario).
  RQ: removing seniors (Sr=0) starves training; future Sr+Ment lags.
  Hypothesis basis: Sr * mentor_rate IS the only inflow back into Jr;
  set Sr=0 and the Jr -> Tr -> Sr conveyor empties without refill."""
  init = {'Jr':[20,0,100,'devs'], 'Tr':[5,0,100,'devs'],
          'Sr':[5,0,100,'devs'], 'Ment':[0,0,100,'mentor-slots'],
          'train_rate':[0.10,0,1,'frac/tick'],
          'promote_rate':[0.05,0,1,'frac/tick'],
          # Mentor capacity: junior recruits per senior per tick.
          # Closes the loop back to Jr.
          'mentor_rate':[0.02,0,1,'items/sr/tick']}

  def step(dt, t, u, v):
    train   = u.Jr * u.train_rate
    promote = u.Tr * u.promote_rate
    # mentor flow returns seniors' mentor-capacity to Jr (recruiting).
    # Same scalar is added to Ment to track cumulative mentor-effort.
    mentor  = u.Sr * u.mentor_rate
    v.Jr   = u.Jr   - dt * train + dt * mentor
    v.Tr   = u.Tr   + dt * (train - promote)
    v.Sr   = u.Sr   + dt * (promote - mentor)
    v.Ment = u.Ment + dt * mentor
    for p in ('train_rate','promote_rate','mentor_rate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Pipeline health = final senior count + cumulative mentor output.
    # Sr alone would miss the early-mentor contribution.
    end = out[-1][1]
    return end.Sr + end.Ment

  def rq(bg=None):
    # 'down' = treated (Sr=0) WORSE than baseline (Sr=5). With Sr=0,
    # the mentor loop is open at the inflow, draining Jr without refill.
    bi = init if bg is None else bg
    return verdict("Sr=0 starves training pipeline",
                   y(run({**bi, 'Sr':[5,0,100,'devs']}, step)),
                   y(run({**bi, 'Sr':[0,0,100,'devs']}, step)), 'down')

  return Model(init, step, y, rq, 'Sr')


def brooksq():
  """Brooks [1] + Madachy [7]: late hires hurt quality-adjusted progress.
  The velocity-only brooks model misses Brooks's quality claim: new
  hires both work slower (training drag) AND inject more bugs that leak
  to the field. This model adds two stocks (Bugs, Esc) and two rate
  params (inj_rate, leak_rate) on top of brooks's structure.

  Stocks: Vet, New, Done, Todo, Bugs, Esc. y = Done - 5*Esc (escaped
  bugs are 5x worse than open work).
  Control: boost (size of late-hire shock at t=10).
  RQ: a boost=10 cohort reduces y vs boost=0 — the compound velocity +
  quality drag is the brooksq claim that brooks alone can't express."""
  init = {'Vet':[10,0,100,'devs'], 'New':[0,0,100,'devs'],
          'Done':[0,0,500,'items'], 'Todo':[500,0,500,'items'],
          'Bugs':[0,0,100,'bugs'], 'Esc':[0,0,100,'bugs'],
          # ctrl: late-hire shock at t=10
          'boost':[0,0,100,'devs'],
          # Same comm + train coefficients as brooks
          'comm_coef':[0.005,0,0.05,'frac/pair'],
          'train_coef':[0.2,0,1,'frac/newhire'],
          'prod_rate':[5,0.1,20,'items/vet/tick'],
          # Bug injection per item shipped — quality side of brooksq
          'inj_rate':[0.05,0,0.5,'bugs/item'],
          # Fraction of Bugs that escape to Esc per tick (NOT caught
          # in review). hi=0.5 is the published bound — known F1
          # boundary violation: real OSS projects exceed this.
          'leak_rate':[0.10,0,0.5,'frac'],
          'mature_rate':[0.1,0,1,'frac/tick']}

  def step(dt, t, u, v):
    # Same comm + train + prod as brooks (see that model for derivation).
    comm  = u.Vet * (u.Vet - 1) / 2 * u.comm_coef
    train = u.New * u.train_coef
    prod  = u.Vet * (1 - comm - train) * u.prod_rate
    # Bugs are injected per item shipped (clamp prod >=0 first so that
    # NEGATIVE productivity does not paradoxically *remove* bugs).
    inj   = max(0, prod) * u.inj_rate
    # Bugs in-flight either get caught (drop off Bugs implicitly) or
    # leak to Esc (escape to field). leak_rate is the unhappy share.
    leak  = u.Bugs * u.leak_rate
    v.Todo = u.Todo - dt * max(0, prod)
    v.Done = u.Done + dt * max(0, prod)
    v.New  = u.New - dt * u.mature_rate * u.New + (u.boost if t == 10 else 0)
    v.Vet  = u.Vet + dt * u.mature_rate * u.New
    v.Bugs = u.Bugs + dt * (inj - leak)
    v.Esc  = u.Esc  + dt * leak
    for p in ('boost','comm_coef','train_coef','prod_rate','inj_rate',
              'leak_rate','mature_rate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Quality-adjusted progress: escaped bugs are 5x worse than open work.
    # The 5x weighting is what makes brooksq differ from brooks in spirit.
    end = out[-1][1]
    return end.Done - 5 * end.Esc

  def rq(bg=None):
    # Two-arm boost=0 vs boost=10. 'down' = boost reduces y. Compound
    # mechanism: more comm overhead + train drag + injected bugs.
    bi = init if bg is None else bg
    return verdict("boost=10 hurts quality-adjusted progress",
                   y(run({**bi, 'boost':[0,0,100,'devs']}, step)),
                   y(run({**bi, 'boost':[10,0,100,'devs']}, step)), 'down')

  return Model(init, step, y, rq, 'boost')


def defmap():
  """Abdel-Hamid & Madnick [5] defect submodel: bugs flow from
  Injected -> Caught (testing finds them) or Injected -> Latent
  (testing misses them) -> Prod (operational failure).

  Stocks: Injected, Caught, Latent, Prod. Production failures (Prod)
  are the worst outcome; Latent is the in-the-wild backlog.
  Control: tst (testing intensity multiplier).
  RQ: dropping tst from 2.5 to 0.5 (less testing) balloons Prod.
  Hypothesis basis: leak = Injected * (1 - tst*detect_coef); halving
  tst shifts the catch/leak split toward leak, which feeds Latent
  and then Prod via the failure rate."""
  init = {'Cmplx':[20,0,100,'complexity'], 'Dsn':[20,0,100,'design-units'],
          'Use':[35,0,100,'usage-units'],
          'Injected':[2.43,0,100,'bugs'], 'Caught':[0,0,100,'bugs'],
          'Latent':[0,0,100,'bugs'], 'Prod':[0,0,100,'items'],
          # ctrl: testing intensity (higher = more bugs caught, fewer leaked)
          'tst':[2.5,0,10,'frac'],
          'intro_c':[0.3,0,1,'bugs/complexity'],
          'intro_d':[0.2,0,1,'bugs/design'],
          'detect_coef':[0.4,0,1,'frac/tst'],
          'fail_coef':[0.15,0,1,'frac/latent']}

  def step(dt, t, u, v):
    # Bug injection has TWO sources with opposite signs: complexity
    # introduces bugs (+), design effort prevents them (-).
    intro  = u.Cmplx * u.intro_c - u.Dsn * u.intro_d
    detect = u.tst * u.Injected * u.detect_coef
    # leak = Injected NOT caught — modeled as a fraction (NOT
    # Injected - detect) so detect_coef and leak share the same
    # arithmetic basis.
    leak   = u.Injected * (1 - u.tst * u.detect_coef)
    fail   = u.Latent * u.Use * u.fail_coef
    v.Injected = u.Injected + dt * intro
    v.Caught   = u.Caught   + dt * detect
    v.Latent   = u.Latent   + dt * (leak - fail)
    v.Prod     = u.Prod     + dt * fail
    for p in ('Cmplx','Dsn','Use','tst','intro_c','intro_d',
              'detect_coef','fail_coef'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Both Prod (released defects) and Latent (lurking) hurt y, with
    # Latent at half the weight (not yet harmful, but a future risk).
    end = out[-1][1]
    return -end.Prod - 0.5 * end.Latent

  def rq(bg=None):
    # 'down' = treated (tst=0.5) WORSE than baseline (tst=2.5).
    # Reduced testing means more leaks -> more Latent -> more Prod.
    bi = init if bg is None else bg
    return verdict("tst=0.5 increases operational defects",
                   y(run({**bi, 'tst':[2.5,0,10,'frac']}, step)),
                   y(run({**bi, 'tst':[0.5,0,10,'frac']}, step)), 'down')

  return Model(init, step, y, rq, 'tst')


def aiwork():
  """GitClear [8] / METR [9]: AI-assisted coding has a quality tradeoff.
  AI boosts raw generation rate but inflates churn (code rewritten or
  abandoned) AND adds verification drag (humans must check outputs).
  Net effect on KEPT code (the thing that ships) is ambiguous.

  Stocks: Todo -> Wip -> {Kept, Churned}. Kept is the success measure.
  Control: ai (0=no AI, 1=full AI). RQ: ai=1 lowers final Kept.
  Hypothesis from METR 2025: AI accelerates throughput at the cost of
  more rework, so the net signed effect on Kept can be negative."""
  init = {'Todo':[1000,0,1000,'items'], 'Wip':[0,0,500,'items'],
          'Kept':[0,0,1000,'items'], 'Churned':[0,0,1000,'items'],
          # ctrl: AI usage fraction across the team
          'ai':[0,0,1,'frac'],
          # Per-unit-AI effect coefficients (literature priors, wide ranges)
          'gen_boost':[0.3,0,2,'frac/ai'],     # +30% gen at full AI
          'churn_mult':[2.0,0,5,'frac/ai'],    # 3x churn at full AI
          'verify_drag':[0.4,0,1,'frac/ai'],   # 40% time on verification at full AI
          'mature_rate':[0.2,0,1,'frac/tick'], # Wip -> Kept transition rate
          'churn_base':[0.05,0,1,'frac/tick']} # baseline (no-AI) churn rate

  def step(dt, t, u, v):
    # Three AI effects (multiplicative on baseline rates):
    gen_boost   = 1 + u.gen_boost * u.ai     # speedup factor
    churn_mult  = 1 + u.churn_mult * u.ai    # churn inflation factor
    verify_drag = u.verify_drag * u.ai       # fraction of capacity spent verifying
    # Net gen = baseline_rate (10/tick) * speedup * (1 - verify overhead).
    # When verify_drag=1 (all AI, all time on review) gen collapses to 0.
    gen   = 10 * gen_boost * (1 - verify_drag)
    add   = min(gen, u.Todo)                 # cap: can't pull from empty Todo
    mature = u.Wip * u.mature_rate           # Wip -> Kept
    churn  = u.Wip * u.churn_base * churn_mult  # Wip -> Churned (lossy)
    v.Todo    = u.Todo - dt * add
    v.Wip     = u.Wip + dt * (add - mature - churn)
    v.Kept    = u.Kept + dt * mature
    v.Churned = u.Churned + dt * churn
    # Carry params forward (rates are stateless across ticks):
    for p in ('ai','gen_boost','churn_mult','verify_drag',
              'mature_rate','churn_base'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Success = final Kept. Churned doesn't count (rewritten/abandoned).
    return out[-1][1].Kept

  def rq(bg=None):
    # Two-arm comparison: ai=0 (baseline) vs ai=1 (full AI adoption).
    # 'down' expected: AI's churn + verify drag should outweigh gen boost,
    # producing LESS final Kept than the baseline.
    bi = init if bg is None else bg
    return verdict("ai=1 reduces Kept (METR/GitClear)",
                   y(run({**bi, 'ai':[0,0,1,'frac']}, step)),
                   y(run({**bi, 'ai':[1,0,1,'frac']}, step)), 'down')

  return Model(init, step, y, rq, 'ai')


def flaky():
  """Luo et al. [11]: flaky tests erode trust which erodes coverage.
  When tests flake, devs stop writing new tests AND stop trusting
  existing ones. Bugs leak through the resulting coverage gap.

  Stocks: Tests (reliable), Flakes (unreliable), Bugs (leaked).
  Control: flake_rate (per-tick probability a test becomes flaky).
  RQ: flake_rate 0.10 (vs 0.02) erodes useful coverage.
  Hypothesis basis: cover = Tests/(Tests+Flakes) gates BOTH new test
  investment (positive feedback dies) and flake-fixing — high flake_rate
  spirals the system toward the all-Flakes attractor."""
  init = {'Tests':[100,0,500,'tests'], 'Flakes':[5,0,500,'tests'],
          'Bugs':[0,0,500,'bugs'],
          # ctrl: per-tick probability a reliable test goes flaky
          'flake_rate':[0.02,0,0.2,'frac/tick'],
          'invest_base':[5,0,20,'frac/tick'],
          'fix_coef':[0.15,0,1,'frac/flake'],
          'leak_coef':[3,0,10,'frac/flake']}

  def step(dt, t, u, v):
    # Coverage health = share of reliable tests. Drives both new test
    # investment (positive feedback) AND flake-fixing throughput.
    cover = u.Tests / max(1, u.Tests + u.Flakes)
    add   = u.invest_base * cover
    flake = u.Tests * u.flake_rate
    fix   = u.Flakes * u.fix_coef * cover
    # Leak = share of unreliable tests * coefficient. Higher Flake share
    # means more bugs slip past testing.
    leak  = u.Flakes / max(1, u.Tests + u.Flakes) * u.leak_coef
    v.Tests = u.Tests + dt * (add - flake)
    v.Flakes = u.Flakes + dt * (flake - fix)
    v.Bugs = u.Bugs + dt * leak
    for p in ('flake_rate','invest_base','fix_coef','leak_coef'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Useful coverage net of damage = reliable tests minus bugs leaked.
    end = out[-1][1]
    return end.Tests - end.Bugs

  def rq(bg=None):
    # 'down' = treated (flake_rate=0.10) WORSE; coverage erodes faster.
    bi = init if bg is None else bg
    return verdict("high flake_rate erodes useful coverage",
                   y(run({**bi, 'flake_rate':[0.02,0,0.2,'frac/tick']}, step)),
                   y(run({**bi, 'flake_rate':[0.10,0,0.2,'frac/tick']}, step)), 'down')

  return Model(init, step, y, rq, 'flake_rate')


def dora():
  """Forsgren, Humble, Kim [12] DORA four keys: deploy frequency,
  lead time, change-fail rate (CFR), mean-time-to-recovery (MTTR).
  Large batches inflate CFR; incidents drain recovery capacity which
  in turn caps future deploys.

  Stocks: Wip, Deploys (cumulative), Incidents, Recovery (in-flight
  recovery cost).
  Control: batch_size (items per release).
  RQ: batch_size 50 (vs 5) reduces net deploys (penalised by incidents).
  Hypothesis basis: large batches -> high CFR -> Recovery accumulates
  -> capacity term `1 - Recovery/50` drops -> fewer deploys possible."""
  init = {'Wip':[100,0,500,'items'], 'Deploys':[0,0,200,'deploys'],
          'Incidents':[0,0,100,'incidents'],
          'Recovery':[0,0,200,'ticks'],
          # ctrl: items per release
          'batch_size':[10,1,100,'items/release'],
          'cfr_coef':[0.005,0,0.1,'frac/batch'],
          'arrival_rate':[8,0,50,'items/tick'],
          'rec_rate':[0.3,0,1,'frac/tick']}

  def step(dt, t, u, v):
    # CFR ~ batch_size (DORA's central finding) clamped at 50%.
    cfr     = min(0.5, u.batch_size * u.cfr_coef)
    # Capacity drops as outstanding Recovery work piles up. Floor 0.1
    # so a team that's drowning still ships SOMETHING.
    cap     = max(0.1, 1 - u.Recovery / 50)
    # Deploys = batches available, capped at 5/tick (throughput ceiling)
    # and scaled by remaining capacity.
    deploys = min(u.Wip / max(1, u.batch_size), 5) * cap
    new_inc = deploys * cfr
    rec     = u.Incidents * u.rec_rate
    # Recovery accrues 2 units per incident (asymmetric cost) and
    # decays at 40%/tick once underway.
    v.Wip       = u.Wip - dt * deploys * u.batch_size + dt * u.arrival_rate
    v.Deploys   = u.Deploys + dt * deploys
    v.Incidents = u.Incidents + dt * (new_inc - rec)
    v.Recovery  = u.Recovery + dt * (new_inc * 2 - u.Recovery * 0.4)
    for p in ('batch_size','cfr_coef','arrival_rate','rec_rate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Net deploys minus 2x incident cost (incidents twice as bad as
    # an extra deploy is good — captures DORA's outage premium).
    end = out[-1][1]
    return end.Deploys - 2 * end.Incidents

  def rq(bg=None):
    # 'down' = treated (batch_size=50) WORSE; CFR up, capacity down.
    bi = init if bg is None else bg
    return verdict("batch_size=50 hurts net deploys",
                   y(run({**bi, 'batch_size':[5,1,100,'items/release']}, step)),
                   y(run({**bi, 'batch_size':[50,1,100,'items/release']}, step)), 'down')

  return Model(init, step, y, rq, 'batch_size')


def micro():
  """Newman [14]: services grow linearly but dependencies grow
  quadratically (each new service can talk to all existing ones).
  Past a coupling threshold, integration cost eats throughput.

  Stocks: Services, Deps, Feat (shipped features).
  Control: coupling_rate (new deps per new service).
  RQ: high coupling_rate (3.0 vs 0.5) erodes throughput.
  Hypothesis basis: density = Deps/Services^2; fps drops as density
  rises, even though Services keeps growing — Newman's "monolith with
  HTTP" warning."""
  init = {'Services':[5,1,100,'services'], 'Deps':[5,0,500,'deps'],
          'Feat':[0,0,500,'items'],
          # ctrl: dependencies created per new service per tick
          'coupling_rate':[1.5,0,5,'deps/svc/tick'],
          'svc_growth':[0.5,0,5,'svcs/tick']}

  def step(dt, t, u, v):
    new_svc  = u.svc_growth
    # New deps scale with existing service count (Services/5 keeps the
    # default scale around 1.0 — each new svc roughly couples to
    # all the existing ones).
    new_deps = new_svc * u.coupling_rate * (u.Services / 5)
    # Density = deps per (svc-pair). At density=0.5, throughput halves.
    density  = u.Deps / max(1, u.Services * u.Services)
    # Floor 0.1 prevents total collapse (the team still ships SOMETHING).
    fps      = max(0.1, u.Services * (1 - 2 * density))
    v.Services = u.Services + dt * new_svc
    v.Deps     = u.Deps + dt * new_deps
    v.Feat     = u.Feat + dt * fps
    v.coupling_rate, v.svc_growth = u.coupling_rate, u.svc_growth

  def y(out):
    return out[-1][1].Feat

  def rq(bg=None):
    # 'down' = treated (coupling_rate=3.0) WORSE; deps grow fast
    # enough to dominate the service-count benefit.
    bi = init if bg is None else bg
    return verdict("high coupling_rate erodes throughput",
                   y(run({**bi, 'coupling_rate':[0.5,0,5,'deps/svc/tick']}, step)),
                   y(run({**bi, 'coupling_rate':[3.0,0,5,'deps/svc/tick']}, step)), 'down')

  return Model(init, step, y, rq, 'coupling_rate')


def teamtopo():
  """Skelton & Pais [13]: cognitive load per team determines delivery
  capacity. load = Domain/team; past load_thresh the team's throughput
  starts collapsing.

  Stocks: Domain (size grows on its own), Delivered.
  Control: Domain (initial domain scope assigned to the team).
  RQ: oversized initial Domain (20 vs 5) collapses delivery.
  Hypothesis basis: thr drops as (load - load_thresh) grows; collapse
  is gated by collapse_coef so the regime boundary is sharp."""
  init = {'Domain':[5,0,50,'domain-units'],
          'Delivered':[0,0,500,'items'],
          'team':[7,1,20,'devs'],
          # Past load_thresh items per team, cognitive load begins
          # collapsing throughput (Skelton & Pais "team-as-bottleneck").
          'load_thresh':[1.5,0.1,5,'items/team'],
          'domain_growth':[0.3,0,2,'domain/tick'],
          'collapse_coef':[0.8,0,2,'frac/overload']}

  def step(dt, t, u, v):
    load = u.Domain / max(1, u.team)
    # Throughput = team headcount * remaining capacity, where capacity
    # falls linearly with overload past load_thresh and floors at 0.
    thr  = u.team * max(0, 1 - max(0, load - u.load_thresh) * u.collapse_coef)
    v.Domain    = u.Domain + dt * u.domain_growth
    v.Delivered = u.Delivered + dt * thr
    for p in ('team','load_thresh','domain_growth','collapse_coef'):
      setattr(v, p, getattr(u, p))

  def y(out):
    return out[-1][1].Delivered

  def rq(bg=None):
    # 'down' = treated (Domain=20) WORSE; load past threshold, capacity
    # collapses faster than headcount can absorb.
    bi = init if bg is None else bg
    return verdict("oversized Domain collapses delivery",
                   y(run({**bi, 'Domain':[5,0,50,'domain-units']}, step)),
                   y(run({**bi, 'Domain':[20,0,50,'domain-units']}, step)), 'down')

  return Model(init, step, y, rq, 'Domain')


def burnout():
  """DORA wellbeing [15]: chronic overload erodes capacity. Workload
  past capacity raises Stress; Stress erodes Capacity. The compound
  feedback can spiral into reduced delivery even at steady workload.

  Stocks: Capacity, Stress, Delivered.
  Control: workload (sustained hours/dev/tick demanded of the team).
  RQ: workload=60 (vs 40) erodes net delivery.
  Hypothesis basis: excess = workload - Capacity > 0 raises Stress;
  Stress feeds back through erode_coef to drop Capacity; the loop
  closes only via recover_coef (slow Stress decay)."""
  init = {'Capacity':[40,10,50,'h/dev'],
          'Stress':[0,0,100,'stress-units'],
          'Delivered':[0,0,2000,'items'],
          # ctrl: weekly hours demanded per dev
          'workload':[40,0,100,'h/dev/tick'],
          'stress_coef':[1.0,0,5,'stress/h'],
          'recover_coef':[0.05,0,1,'frac/tick'],
          'erode_coef':[0.05,0,1,'frac/stress']}

  def step(dt, t, u, v):
    # Actual work delivered is capped at Capacity; any excess
    # accumulates as Stress (the unhappy share of demand).
    actual  = min(u.workload, u.Capacity)
    excess  = max(0, u.workload - u.Capacity)
    d_stress = excess * u.stress_coef - u.Stress * u.recover_coef
    # Capacity erodes under Stress AND recovers toward 40h baseline.
    # The (40 - Capacity)*0.1 term is mean-reverting healing when stress is low.
    d_cap    = -u.Stress * u.erode_coef + max(0, 40 - u.Capacity) * 0.1
    v.Capacity  = u.Capacity + dt * d_cap
    v.Stress    = u.Stress + dt * d_stress
    v.Delivered = u.Delivered + dt * actual
    for p in ('workload','stress_coef','recover_coef','erode_coef'):
      setattr(v, p, getattr(u, p))

  def y(out):
    return out[-1][1].Delivered

  def rq(bg=None):
    # 'down' = treated (workload=60) WORSE; chronic excess builds
    # Stress -> erodes Capacity -> actual work falls below baseline.
    bi = init if bg is None else bg
    return verdict("workload=60 erodes net delivery",
                   y(run({**bi, 'workload':[40,0,100,'h/dev/tick']}, step)),
                   y(run({**bi, 'workload':[60,0,100,'h/dev/tick']}, step)), 'down')

  return Model(init, step, y, rq, 'workload')


def aidebt():
  """Cunningham [3] + GitClear [8]: AI-coded features carry more debt
  per unit shipped, even when AI speeds up gen. The model layers an
  AI multiplier on debt's born_rate over top of the debt() structure.

  Stocks: Feat, Debt, Vel (same as debt). Control: ai in [0,1].
  RQ: ai=1 raises Debt enough to depress y = Feat - mean(Debt).
  Hypothesis basis: born_rate = born_base*(1+born_ai_mult*ai); even
  with gen_ai_mult acceleration, the per-item debt cost can grow faster.

  Findings (VV 2026-06-03 grid sweep): the May 11 ~1.5x leverage-ratio
  crossover claim does NOT reproduce. Regime is TEMPORAL — REFUTE
  dominates at tmax 10-30 (AI helps); CONFIRM 99% at tmax 50-80 (AI
  hurts). See `paper/outputs/grid_aidebt_*.csv`."""
  init = {'Feat':[1,0,200,'items'], 'Debt':[0,0,100,'debt-items'],
          'Vel':[10,0,20,'items/tick'],
          # ctrl: AI adoption fraction
          'ai':[0,0,1,'frac'],
          # Baseline debt per unit shipped (no-AI)
          'born_base':[0.3,0,1,'debt/tick'],
          # AI debt multiplier — May 11 claim was 1.5x = "AI doubles debt"
          'born_ai_mult':[1.5,0,5,'frac/ai'],
          # AI gen-rate multiplier — speeds shipping
          'gen_ai_mult':[0.3,0,2,'frac/ai'],
          'intr_rate':[0.10,0,0.5,'frac/tick'],
          'pay_rate':[0.15,0,1,'frac/tick']}

  def step(dt, t, u, v):
    # debt's debt-velocity feedback, plus AI gen speedup as a third
    # multiplicative factor on ship.
    speed = max(0, 1 - u.Debt / 100)
    ship  = (1 + u.Feat * 0.1) * speed * (1 + u.gen_ai_mult * u.ai)
    # rate = born_base * (1 + born_ai_mult * ai) — AI inflates the
    # per-shipped-unit debt accrual. This is the gear that turns the
    # leverage-ratio claim.
    rate  = u.born_base * (1 + u.born_ai_mult * u.ai)
    born  = ship * rate
    intr  = u.Debt * u.intr_rate
    pay   = u.Debt * u.pay_rate
    v.Feat = u.Feat + dt * ship
    v.Debt = u.Debt + dt * (born + intr - pay)
    v.Vel  = 10 * speed
    for p in ('ai','born_base','born_ai_mult','gen_ai_mult',
              'intr_rate','pay_rate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    end = out[-1][1]
    md = sum(r.Debt for _, r in out) / len(out)
    return end.Feat - md

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("ai=1 raises debt > offsets feature speedup",
                   y(run({**bi, 'ai':[0,0,1,'frac']}, step)),
                   y(run({**bi, 'ai':[1,0,1,'frac']}, step)), 'down')

  return Model(init, step, y, rq, 'ai')


def archpat():
  """Architectural patterns as repair: Martin Clean Arch [16] + Perry-Wolf [17].
  
  Tests architect's claim: 'patterns repair existing-bad-software'.
  
  Three regions: Patterned (under good architecture), Legacy (not), Drift
  (was patterned, eroded). Migration moves Legacy -> Patterned at rate
  proportional to migrate_rate * available effort. Decay moves Patterned
  -> Drift at rate decay_rate (architectural erosion: Perry & Wolf 1992).
  Drift converts back to Legacy at a fixed rate.
  
  Debt accumulates in both regions but at different rates: legacy code
  generates more debt per feature than patterned code (factor pat_strength).
  
  RQ: starting from Patterned=10, Legacy=90, Debt=40 (already-bad project),
  does aggressive migration (migrate=1.5) actually repair the project
  vs slow migration (migrate=0.2)?  architect's strong claim says yes.
  """
  init = {'Patterned':[10,0,1000,'modules'], 'Legacy':[90,0,3000,'modules'],
          'Drift':[0,0,200,'modules'], 'Debt':[40,0,150,'debt-items'], 'Feat':[0,0,2000,'items'],
          'migrate':[0.2,0,2,'frac/tick'], 'decay_rate':[0.05,0,0.5,'frac/tick'],
          'drift_to_legacy':[0.10,0,1,'frac/tick'],
          'gen_pat':[1.0,0.1,3,'items/pat/tick'], 'gen_leg':[0.4,0.1,3,'items/leg/tick'],
          'born_pat':[0.05,0,1,'debt/pat/tick'], 'born_leg':[0.20,0,1,'debt/leg/tick'],
          'intr_rate':[0.08,0,0.5,'frac/tick'], 'pay_rate':[0.15,0,1,'frac/tick'],
          'pat_strength':[4,1,10,'frac']}

  def step(dt, t, u, v):
    speed     = max(0.05, 1 - u.Debt / 150)
    available = (u.Patterned + u.Legacy + u.Drift) * speed
    # migration: legacy -> patterned (costs effort proportional to migrate)
    migration_flow = u.migrate * u.Legacy * 0.05
    # decay: patterned -> drift (architectural erosion)
    decay_flow = u.decay_rate * u.Patterned
    # drift -> legacy (drift fully converts back over time)
    drift_flow = u.drift_to_legacy * u.Drift
    # feature generation (Drift acts like Legacy for shipping)
    gen = (u.Patterned * u.gen_pat
           + (u.Legacy + u.Drift) * u.gen_leg) * speed
    # debt: legacy code generates more debt per feature
    pat_share = u.Patterned / max(1, u.Patterned + u.Legacy + u.Drift)
    born = gen * (u.born_pat * pat_share + u.born_leg * (1 - pat_share))
    intr = u.Debt * u.intr_rate
    pay  = u.Debt * u.pay_rate * (1 + 0.5 * pat_share)  # patterns help paydown
    v.Patterned = u.Patterned + dt * (migration_flow - decay_flow)
    v.Legacy    = u.Legacy    - dt * migration_flow + dt * drift_flow
    v.Drift     = u.Drift     + dt * (decay_flow - drift_flow)
    v.Debt      = u.Debt      + dt * (born + intr - pay)
    v.Feat      = u.Feat      + dt * gen
    for p in ('migrate','decay_rate','drift_to_legacy','gen_pat','gen_leg',
              'born_pat','born_leg','intr_rate','pay_rate','pat_strength'):
      setattr(v, p, getattr(u, p))

  def y(out):
    """Reward features delivered, penalize sustained debt."""
    end = out[-1][1]
    md = sum(r.Debt for _, r in out) / len(out)
    return end.Feat - md

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("aggressive migration repairs already-bad project",
                   y(run({**bi, 'migrate':[0.2,0,2,'frac/tick']}, step)),
                   y(run({**bi, 'migrate':[1.5,0,2,'frac/tick']}, step)), 'up')

  return Model(init, step, y, rq, 'migrate')


def congruence():
  """**Smells-based variant** of socio-technical congruence (kaiaulu
  R/smells.R lineage; Catolino 2019, IEEE 8651329). Newman [14] /
  radio-silence (coder et al.): boundary-spanning brokers hold
  communication-fragmented projects together.

  Companion model `congruence_motif` (motif-based STC variant per
  Mauerer/Joblin/Paradis/Kazman/Apel TSE 48(8) 2022) is TODO UU
  in `TODO.md`. Together they form the methodology paper's
  same-thesis / different-operationalization pair.

  Stocks: Clusters (sub-communities), Brokers (devs spanning them),
  Cohesion (cumulative coherent work).
  Control: broker_loss (per-tick attrition of brokers).
  RQ: broker_loss=0.3 (vs 0) fragments project, hurts cohesion.
  Hypothesis basis: brokers cap Cluster fragmentation; lose them and
  the fragmentation feedback runs away."""
  init = {'Clusters':[5,1,20,'clusters'], 'Brokers':[3,0,20,'devs'],
          'Cohesion':[0,0,500,'cohesion'],
          # ctrl: per-tick fraction of brokers lost
          'broker_loss':[0,0,1,'frac/tick'],
          'broker_form':[0.05,0,0.5,'frac/tick'],
          # Fragmentation rate, only active when Clusters > Brokers
          # (brokers can't span enough; new clusters split off)
          'fragment_rate':[0.05,0,0.5,'frac/tick'],
          'merge_rate':[0.1,0,0.5,'frac/tick'],
          'work_rate':[5,0,20,'cohesion/broker/tick']}

  def step(dt, t, u, v):
    # Brokers form proportional to inter-cluster gradient, drain by ctrl.
    form  = u.broker_form * u.Clusters
    drain = u.broker_loss * u.Brokers
    # Fragmentation only kicks in when there are MORE clusters than
    # brokers — i.e. brokers ARE the cap on community splintering.
    frag  = u.fragment_rate * max(0, u.Clusters - u.Brokers)
    merge = u.merge_rate * u.Brokers
    # Cohesion gain scales with broker coverage per cluster — a project
    # with 5 clusters and 5 brokers still works; 5 clusters / 1 broker
    # doesn't.
    coh_gain = u.work_rate * (u.Brokers / max(1, u.Clusters))
    # max(0, ...) and max(1, ...) clamps: prevent negative Brokers and
    # zero Clusters (zero would div-by-zero on the next tick).
    v.Brokers  = max(0, u.Brokers  + dt * (form - drain))
    v.Clusters = max(1, u.Clusters + dt * (frag - merge))
    v.Cohesion = u.Cohesion + dt * coh_gain
    for p in ('broker_loss','broker_form','fragment_rate',
              'merge_rate','work_rate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Reward final Cohesion, penalise fragmentation (5x per cluster).
    # 5x weight: cluster count is small but each new cluster is a big
    # coordination cost.
    end = out[-1][1]
    return end.Cohesion - 5 * end.Clusters

  def rq(bg=None):
    # 'down' = treated (broker_loss=0.3) WORSE; without brokers the
    # cluster count grows unchecked, draining per-cluster broker cover.
    bi = init if bg is None else bg
    return verdict("broker_loss=0.3 fragments project, hurts cohesion",
                   y(run({**bi, 'broker_loss':[0.0,0,1,'frac/tick']}, step)),
                   y(run({**bi, 'broker_loss':[0.3,0,1,'frac/tick']}, step)), 'down')

  return Model(init, step, y, rq, 'broker_loss')


def congruence_motif():
  """**Motif-based variant** of socio-technical congruence (STC).
  Companion to the smells-based `congruence` model above.

  Source: Mauerer, Joblin, Tamburri, Paradis, Kazman, Apel (2022).
  "In Search of Socio-Technical Congruence: A Large-Scale
  Longitudinal Study." IEEE TSE 48(8):3159-3184.
  doi:10.1109/TSE.2021.3082074. Operationalized in kaiaulu
  R/motif.R via igraph::count_subgraph_isomorphisms over four
  motif templates.

  Thesis (Cataldo/Mauerer): dev-pairs who CO-TOUCH source files
  (or dep-linked files) SHOULD COMMUNICATE about it. When they
  don't, anti-motif counts (anti-triangle, anti-square) accumulate.
  Anti-motifs realize the coordination gap as defects.

  Motif accounting per tick:
    Triangle      = pair comm + co-touch file        (positive)
    Anti-Triangle = pair NO-comm + co-touch file     (negative)
    Square        = pair comm + co-touch dep-linked  (positive)
    Anti-Square   = pair NO-comm + co-touch dep-linked (negative)

  Stocks: Devs, Files, Bugs (success = LOW final Bugs).
  Ctrl: comm_rate. RQ: high comm (0.8) reduces Bugs vs low comm (0.2).

  Lift (per project, per snapshot, via kaiaulu motif_factory +
  igraph::count_subgraph_isomorphisms over the merged
  git-reply-dependency network): produces Tri/AntiTri/Sq/AntiSq
  integer counts plus n_devs, n_files, n_deps. Calibrate `comm_rate`
  from the empirical ratio (Tri+Sq)/(all four)."""
  init = {'Devs':[30,2,200,'devs'], 'Files':[100,10,5000,'files'],
          'Bugs':[0,0,500,'bugs'],
          # ctrl: probability a co-touching dev-pair communicates
          'comm_rate':[0.5,0,1,'frac'],
          # Network params (literature priors):
          'dep_density':[0.2,0,1,'frac/pair'],         # cross-file dep frequency
          'pair_touch_rate':[0.05,0,1,'frac/pair/tick'],  # avg co-touch frequency
          # Bug accounting:
          'bug_per_antimotif':[0.5,0,5,'bugs/event'],
          'bug_pay_rate':[0.1,0,1,'frac/tick']}

  def step(dt, t, u, v):
    # Mauerer 2022 motif accounting at flow level:
    # enumerate dev-pairs that could co-touch this tick.
    active_pairs = u.Devs * (u.Devs - 1) / 2 * u.pair_touch_rate
    # Of those, the fraction that DON'T communicate become anti-triangles.
    antitri_flow = active_pairs * (1 - u.comm_rate)
    # Subset of pairs that touch DEP-LINKED file pairs (square family).
    cross_pairs  = active_pairs * u.dep_density
    antisq_flow  = cross_pairs * (1 - u.comm_rate)
    # Each anti-motif event accrues some Bugs; refactor pays them down.
    bugs_born = (antitri_flow + antisq_flow) * u.bug_per_antimotif
    bugs_paid = u.Bugs * u.bug_pay_rate
    v.Devs  = u.Devs
    v.Files = u.Files
    v.Bugs  = max(0, u.Bugs + dt * (bugs_born - bugs_paid))
    for p in ('comm_rate','dep_density','pair_touch_rate',
              'bug_per_antimotif','bug_pay_rate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Final Bugs is the success measure. Lower = better.
    # rq() uses expect='down' so CONFIRM means y1 < y0 (more comm → fewer Bugs).
    return out[-1][1].Bugs

  def rq(bg=None):
    # Two-arm comparison: low comm (0.2, communication-fragmented)
    # vs high comm (0.8, well-coordinated). Mauerer's thesis says
    # the high-comm arm produces fewer defects via fewer anti-motifs.
    bi = init if bg is None else bg
    return verdict("comm_rate 0.8 reduces Bugs vs 0.2 (Mauerer 2022 STC)",
                   y(run({**bi, 'comm_rate':[0.2,0,1,'frac']}, step)),
                   y(run({**bi, 'comm_rate':[0.8,0,1,'frac']}, step)), 'down')

  return Model(init, step, y, rq, 'comm_rate')


# --- 15 candidate models lifted from docs/other.html (buildable today) -------


def little():
  """Little (1961) "A Proof for the Queuing Formula L = λW."
  Queueing identity: long-run WIP = throughput * cycle_time. Acts as
  a process-physics sanity check on any flow-based dev model.

  Stocks (UPPER):
    WIP     : work-in-progress items currently inside the system
    Arrival : per-tick arrival rate (held constant — the world's input)
    Done    : cumulative items leaving the system
  Params (lower):
    cycle_time : average time each item spends in the system
    wip_cap    : hard ceiling on WIP (Kanban-style policy)

  Thesis: holding Arrival constant, tripling cycle_time (4 -> 12)
  cuts throughput. Pure identity result if the queue is stable."""
  init = {'WIP':[20,0,500,'items'],          # 20 items already in flight at t=0
          'Arrival':[5,0,50,'items/tick'],        # 5 items arrive per tick (steady)
          'Done':[0,0,5000,'items'],         # nothing finished yet
          'cycle_time':[4,1,30,'ticks'],     # *** ctrl ***; 4 ticks per item
          'wip_cap':[60,5,200,'items']}      # WIP can't exceed 60

  def step(dt, t, u, v):
    # Service: clear (WIP / cycle_time) items per tick, but no more than WIP.
    served = min(u.WIP / max(1, u.cycle_time), u.WIP)
    # Intake: accept what arrives, but only up to remaining cap headroom.
    accept = min(u.Arrival, max(0, u.wip_cap - u.WIP))
    # WIP rises by accepted-minus-served. Stable if Arrival == served.
    v.WIP  = u.WIP  + dt * (accept - served)
    # Done strictly grows with served items.
    v.Done = u.Done + dt * served
    for p in ('Arrival','cycle_time','wip_cap'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Reward total work delivered.
    return out[-1][1].Done

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("doubling cycle_time hurts throughput",
                   y(run({**bi, 'cycle_time':[4,1,30,'ticks']},  step)),   # fast
                   y(run({**bi, 'cycle_time':[12,1,30,'ticks']}, step)),   # slow (3x)
                   'down')
  return Model(init, step, y, rq, 'cycle_time')


def coordn2():
  """Brooks (1975 MMM) + Curtis, Krasner, Iscoe (1988 CACM): N
  developers generate N*(N-1)/2 communication pairs. Each pair costs
  developer attention, so doubling the team produces more than
  double the coordination drag.

  Stocks (UPPER):
    Devs : number of developers (held constant per run)
    Done : cumulative work delivered
  Params (lower):
    work_per_dev : base productivity coefficient (items per dev per tick)
    comm_coef    : per-pair attention cost coefficient

  Thesis: doubling Devs (5 -> 10) less than doubles Done (because
  comm_coef * pairs / N grows in N)."""
  init = {'Devs':[5,1,200,'devs'],              # *** ctrl ***; small team default
          'Done':[0,0,10000,'items'],            # nothing done at t=0
          'work_per_dev':[10,0,50,'items/dev/tick'],      # 10 items/dev/tick baseline
          'comm_coef':[0.02,0,0.5,'frac/pair']}      # 2% attention lost per pair-share

  def step(dt, t, u, v):
    # Communication-pair count grows quadratically in team size.
    pairs = u.Devs * (u.Devs - 1) / 2
    # Per-dev tax = (pairs each dev participates in) * coefficient.
    # Cap at 90% to prevent negative throughput at huge N.
    tax   = min(0.9, u.comm_coef * pairs / max(1, u.Devs))
    # Effective output: N devs each producing work_per_dev, minus tax.
    v.Done = u.Done + dt * u.Devs * u.work_per_dev * (1 - tax)
    for p in ('Devs','work_per_dev','comm_coef'):
      setattr(v, p, getattr(u, p))

  def y(out): return out[-1][1].Done

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("doubling team superlinear-taxes throughput",
                   y(run({**bi, 'Devs':[5,1,200,'devs']},  step)),    # small
                   y(run({**bi, 'Devs':[10,1,200,'devs']}, step)),    # doubled
                   'down')
  return Model(init, step, y, rq, 'Devs')


def entropy():
  """Lehman (1980) "Programs, life cycles, and laws of software
  evolution." Continuing change + increasing complexity: software
  entropy rises monotonically unless explicit refactor effort pays
  it down. Without pay-down, complexity grows and defects follow.

  Stocks (UPPER):
    Complexity : intrinsic structural difficulty of the codebase
    Bugs       : cumulative defect count (proportional to complexity)
  Params (lower):
    work_rate     : commit volume per tick (entropy source)
    refactor_rate : fraction of complexity paid down per tick (policy)
    entropy_coef  : how much commit adds to complexity (~0.02)

  Thesis: dropping refactor_rate from 0.20 (active maintenance) to
  0.02 (neglect) inflates terminal Complexity + Bugs."""
  init = {'Complexity':[100,0,5000,'complexity-units'],         # starting complexity
          'Bugs':[0,0,5000,'bugs'],                 # no defects yet
          'work_rate':[10,0,100,'items/tick'],            # 10 commits per tick
          'refactor_rate':[0.05,0,0.5,'frac/tick'],      # *** ctrl ***; 5% paid down
          'entropy_coef':[0.02,0,0.5,'complexity/item']}       # 2% of work becomes complexity

  def step(dt, t, u, v):
    # Each commit adds work_rate * entropy_coef to Complexity.
    grow    = u.work_rate * u.entropy_coef
    # Refactor work removes a fraction of current Complexity.
    pay     = u.Complexity * u.refactor_rate
    # Bug arrival proportional to current Complexity (0.1% per tick).
    bug_in  = u.Complexity * 0.001
    v.Complexity = max(0, u.Complexity + dt * (grow - pay))
    v.Bugs       = u.Bugs + dt * bug_in
    for p in ('work_rate','refactor_rate','entropy_coef'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Reward LOW Complexity AND LOW Bugs. Both negated.
    return -out[-1][1].Complexity - out[-1][1].Bugs

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("low refactor leaves Complexity high",
                   y(run({**bi, 'refactor_rate':[0.20,0,0.5,'frac/tick']}, step)),  # active
                   y(run({**bi, 'refactor_rate':[0.02,0,0.5,'frac/tick']}, step)),  # neglect
                   'down')
  return Model(init, step, y, rq, 'refactor_rate')


def costchange():
  """Boehm (1981) "Software Engineering Economics" cost-of-change
  curve: a bug costs ~$1 in requirements, ~$10 in coding, ~$100 in
  test, ~$1000 in release. Magnitudes have been debated in agile
  contexts but the super-linear shape is consistent across modern
  datasets.

  Stocks (UPPER):
    Bugs : defects still in the system
    Cost : cumulative dollars spent fixing them
  Params (lower):
    catch_early : fraction of bugs caught in cheap phase (policy)
    cost_early  : $ per bug caught early
    cost_late   : $ per bug caught late (typically 50-100x cost_early)

  Thesis: dropping catch_early from 0.8 (test-driven) to 0.2 (ship
  it and fix in prod) inflates total Cost."""
  init = {'Bugs':[20,0,1000,'bugs'],          # 20 outstanding defects
          'Cost':[0,0,1e6,'$'],            # zero spent yet
          'catch_early':[0.6,0,1,'frac'],     # *** ctrl ***; 60% caught early default
          'cost_early':[1,0.1,5,'$/bug'],      # $1 per early catch
          'cost_late':[50,1,500,'$/bug']}      # $50 per late catch (50x ratio)

  def step(dt, t, u, v):
    # Bugs split by phase of discovery this tick.
    e = u.Bugs * u.catch_early
    l = u.Bugs - e
    # Cost integrates phase-weighted fixes.
    v.Cost = u.Cost + dt * (e * u.cost_early + l * u.cost_late)
    # Bugs drain 10% of (early + late) catches per tick (~half-life).
    v.Bugs = max(0, u.Bugs - dt * (e + l) * 0.1)
    for p in ('catch_early','cost_early','cost_late'):
      setattr(v, p, getattr(u, p))

  def y(out): return -out[-1][1].Cost   # reward low Cost

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("shifting catch late inflates total cost",
                   y(run({**bi, 'catch_early':[0.8,0,1,'frac']}, step)),    # test-heavy
                   y(run({**bi, 'catch_early':[0.2,0,1,'frac']}, step)),    # ship-fast
                   'down')
  return Model(init, step, y, rq, 'catch_early')


def pareto():
  """Fenton & Ohlsson (2000 IEEE TSE) + Ostrand & Weyuker (2002 ISSTA):
  ~20% of modules carry ~80% of defects, and that hotspot set persists
  across releases. Implication: allocate fix effort to hotspots, not
  uniformly across the codebase.

  Stocks (UPPER):
    Hot  : hotspot modules (small set, high bug rate)
    Cold : everything else (large set, low bug rate)
    Bugs : current outstanding defect count
  Params (lower):
    hot_bug_rate   : new bugs per hot module per tick
    cold_bug_rate  : new bugs per cold module per tick
    fix_share_hot  : fraction of fix effort sent to hotspots (policy)

  Thesis: dropping fix_share_hot from 0.8 (hotspot-focused) to 0.1
  (proportional/oblivious) inflates Bugs because hot fixes net 4x
  more bug-reduction per unit effort than cold fixes."""
  init = {'Hot':[10,0,200,'modules'],                 # 10 hotspot modules
          'Cold':[90,0,2000,'modules'],               # 90 cold modules (20/80 mix)
          'Bugs':[0,0,5000,'bugs'],                # no outstanding defects yet
          'hot_bug_rate':[0.4,0,2,'bugs/module/tick'],         # hot module: 0.4 bugs/tick
          'cold_bug_rate':[0.02,0,0.5,'bugs/module/tick'],     # cold module: 0.02 bugs/tick
          'fix_share_hot':[0.5,0,1,'frac']}        # *** ctrl ***; 50% effort to hot

  def step(dt, t, u, v):
    # Inflow: bug generation per module class.
    new_hot  = u.Hot  * u.hot_bug_rate
    new_cold = u.Cold * u.cold_bug_rate
    # Outflow: hot fixes are 4x more effective per unit effort (whole
    # point of Pareto allocation).
    fix_hot  = u.fix_share_hot * 8
    fix_cold = (1 - u.fix_share_hot) * 2
    v.Bugs = max(0, u.Bugs + dt * (new_hot + new_cold - fix_hot - fix_cold))
    for p in ('Hot','Cold','hot_bug_rate','cold_bug_rate','fix_share_hot'):
      setattr(v, p, getattr(u, p))

  def y(out): return -out[-1][1].Bugs   # reward low Bugs

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("ignoring hotspots inflates bugs",
                   y(run({**bi, 'fix_share_hot':[0.8,0,1,'frac']}, step)),  # focused
                   y(run({**bi, 'fix_share_hot':[0.1,0,1,'frac']}, step)),  # oblivious
                   'down')
  return Model(init, step, y, rq, 'fix_share_hot')


def linus():
  """Raymond (1999) "Cathedral and the Bazaar" + Mockus, Fielding,
  Herbsleb (2002 ACM TOSEM): "given enough eyeballs, all bugs are
  shallow" — code reviewed by multiple committers shows lower defect
  recurrence than single-author code.

  Stocks (UPPER):
    Open      : unreviewed pull-requests still in the queue
    Reviewed  : merged PRs that received review attention
    Recurring : defects that re-appear after fix because review missed
  Params (lower):
    review_rate : fraction of Open reviewed per tick (policy)
    recur_rate  : base re-occurrence probability when review fails

  Thesis: dropping review_rate from 0.6 (every PR reviewed) to 0.1
  (skim-and-merge) inflates Recurring; net Reviewed - 3*Recurring drops."""
  init = {'Open':[20,0,500,'prs'],            # 20 PRs awaiting review
          'Reviewed':[0,0,5000,'prs'],        # nothing reviewed yet
          'Recurring':[0,0,500,'bugs'],        # no recurrences yet
          'review_rate':[0.4,0,1,'frac/tick'],      # *** ctrl ***; 40% reviewed/tick
          'recur_rate':[0.3,0,1,'frac']}       # 30% base re-occurrence

  def step(dt, t, u, v):
    # Reviewed flow: depends on policy (review_rate) and Open queue size.
    rev = u.Open * u.review_rate
    # Recurrence: scales with reviewed volume but is mitigated by review
    # depth (multiplied by 1-review_rate).
    rec = rev * u.recur_rate * (1 - u.review_rate)
    # Open loses what got reviewed, gains recurrences.
    v.Open      = max(0, u.Open - dt * rev + dt * rec)
    v.Reviewed  = u.Reviewed  + dt * rev
    v.Recurring = u.Recurring + dt * rec
    for p in ('review_rate','recur_rate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Reward reviewed PRs; heavily penalise recurring defects (3x weight).
    return out[-1][1].Reviewed - 3 * out[-1][1].Recurring

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("low review_rate inflates recurrence",
                   y(run({**bi, 'review_rate':[0.6,0,1,'frac/tick']}, step)),    # rigorous
                   y(run({**bi, 'review_rate':[0.1,0,1,'frac/tick']}, step)),    # rubber-stamp
                   'down')
  return Model(init, step, y, rq, 'review_rate')


def mirroring():
  """MacCormack, Baldwin, Rusnak (2006 Mgmt Science) operationalised
  Conway's law: the code's design-structure-matrix (who-calls-who)
  should mirror the organisation's DSM (who-talks-to-who). High
  mirror coefficient predicts clean modular boundaries; low mirror
  predicts coupling churn and defects.

  Stocks (UPPER):
    Modules : file/component count
    Teams   : organisational teams owning subsets of Modules
    Bugs    : cumulative defect count
  Params (lower):
    mirror     : cosine(file-DSM, org-DSM) in [0,1]; policy + structure
    churn_rate : per-tick churn volume (commits/file/tick)

  Thesis: dropping mirror from 0.85 (Conway-aligned) to 0.30
  (cross-team chaos) inflates Bugs because cross-team changes are
  more error-prone."""
  init = {'Modules':[20,1,200,'modules'],          # 20 modules
          'Teams':[5,1,50,'teams'],              # 5 teams
          'Bugs':[0,0,5000,'bugs'],             # no defects yet
          'mirror':[0.7,0,1,'frac'],            # *** ctrl ***; 70% aligned default
          'churn_rate':[2,0,20,'commits/file/tick']}         # 2 commits/file/tick

  def step(dt, t, u, v):
    # Mismatch = 1 - mirror. Drives the leak rate.
    mismatch = (1 - u.mirror)
    # Per-tick bug leak scales with churn AND mismatch.
    leak     = u.churn_rate * mismatch
    # Bugs accumulate with Modules-to-Teams ratio (per-team load).
    v.Bugs   = u.Bugs + dt * leak * u.Modules / max(1, u.Teams)
    for p in ('Modules','Teams','mirror','churn_rate'):
      setattr(v, p, getattr(u, p))

  def y(out): return -out[-1][1].Bugs   # reward low Bugs

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("low mirror inflates defects",
                   y(run({**bi, 'mirror':[0.85,0,1,'frac']}, step)),    # aligned
                   y(run({**bi, 'mirror':[0.30,0,1,'frac']}, step)),    # chaotic
                   'down')
  return Model(init, step, y, rq, 'mirror')


def orgchurn():
  """Nagappan, Murphy, Basili (2008 ICSE) on Windows Vista:
  organisational churn (developer departures, team reorgs) is a
  better predictor of post-release defects than code-churn or
  complexity. Departures carry tacit knowledge with them; gaps
  surface as defects.

  Stocks (UPPER):
    Devs      : active developer count
    Bugs      : cumulative defect count
    knowledge : tacit code-context (a stock that depletes on departure)
  Params (lower):
    churn_rate : per-tick departure fraction (the world's input)

  Thesis: 10x churn_rate spike (0.02 -> 0.20) inflates Bugs because
  knowledge depletes and bug rate scales inversely with knowledge."""
  init = {'Devs':[20,1,500,'devs'],            # 20-dev team default
          'Bugs':[0,0,5000,'bugs'],            # no defects yet
          'churn_rate':[0.02,0,0.5,'frac/tick'],    # *** ctrl ***; 2% departure/tick
          'knowledge':[100,0,1000,'knowledge-units']}     # 100 units of tacit context

  def step(dt, t, u, v):
    # Departures this tick.
    lost = u.Devs * u.churn_rate
    # Devs: lose departures, partially backfilled (50% replacement rate).
    v.Devs      = max(1, u.Devs - dt * lost + dt * lost * 0.5)
    # Knowledge depletes 5 units per departed dev (irreplaceable tacit).
    v.knowledge = max(0, u.knowledge - dt * lost * 5)
    # Bugs scale INVERSELY with current knowledge (low knowledge -> spike).
    v.Bugs      = u.Bugs + dt * (200 / max(1, u.knowledge)) * 10
    setattr(v, 'churn_rate', u.churn_rate)

  def y(out): return -out[-1][1].Bugs   # reward low Bugs

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("departure spike inflates defect burst",
                   y(run({**bi, 'churn_rate':[0.02,0,0.5,'frac/tick']}, step)),  # stable
                   y(run({**bi, 'churn_rate':[0.20,0,0.5,'frac/tick']}, step)),  # 10x churn
                   'down')
  return Model(init, step, y, rq, 'churn_rate')


def ownership():
  """Bird, Nagappan, Murphy, Gall, Devanbu (2011 ESEC/FSE) "Don't
  touch my code!" on Vista + Windows 7: share of MINOR-author
  contributions to a binary correlates strongly with post-release
  defect density. Major-author code is more reliable than
  many-contributor patchwork.

  Stocks (UPPER):
    Modules : module count under study
    Bugs    : cumulative defect count
  Params (lower):
    minor_share   : fraction of commits from non-primary contributors
    major_quality : baseline quality of major-author work [0,1]

  Thesis: raising minor_share from 0.10 (single owner) to 0.60
  (drive-by-heavy) inflates Bugs. Effective quality drops because
  minors are assumed at 60% the quality of majors."""
  init = {'Modules':[50,1,500,'modules'],         # 50 modules
          'Bugs':[0,0,5000,'bugs'],            # no defects yet
          'minor_share':[0.2,0,1,'frac'],      # *** ctrl ***; 20% minor share default
          'major_quality':[0.95,0,1,'frac']}   # major author work is 95% bug-free

  def step(dt, t, u, v):
    # Effective per-module quality = weighted blend of major and minor work.
    # Minor work is fixed at 60% of major quality.
    eff_q = u.major_quality * (1 - u.minor_share) + 0.6 * u.minor_share
    # New bugs per tick: per-module bug rate = (1 - eff_q) * scale.
    new_b = u.Modules * (1 - eff_q) * 0.5
    v.Bugs = u.Bugs + dt * new_b
    for p in ('Modules','minor_share','major_quality'):
      setattr(v, p, getattr(u, p))

  def y(out): return -out[-1][1].Bugs   # reward low Bugs

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("high minor_share inflates defects",
                   y(run({**bi, 'minor_share':[0.10,0,1,'frac']}, step)),   # single-owner
                   y(run({**bi, 'minor_share':[0.60,0,1,'frac']}, step)),   # patchwork
                   'down')
  return Model(init, step, y, rq, 'minor_share')


def ossfail():
  """Coelho & Valente (2017 FSE) "Why modern open source projects
  fail." Survey of 104 dormant/abandoned OSS projects: low truck
  factor (the count of devs whose loss would kill the project) is
  the strongest operational predictor of project death.

  Stocks (UPPER):
    Devs         : active developer count
    Activity     : per-tick development pulse (commits + reviews)
    truck_factor : minimum-k authors who together own >50% of LOC
  Params (lower):
    attrition : background rate at which Activity decays per tick

  Thesis: shrinking truck_factor from 8 (healthy) to 1 (single
  maintainer) accelerates Activity decay; final Activity drops."""
  init = {'Devs':[5,1,200,'devs'],             # 5 devs
          'Activity':[100,0,10000,'activity-units'],     # 100 units pulse at t=0
          'truck_factor':[2,1,20,'devs'],      # *** ctrl ***; TF=2 default
          'attrition':[0.05,0,0.5,'frac/tick']}     # 5%/tick base attrition

  def step(dt, t, u, v):
    # Bus risk = 1 / truck_factor. TF=1 -> risk 1.0; TF=20 -> risk 0.05.
    bus_risk = 1 / max(1, u.truck_factor)
    # Effective decay scales with attrition * (1 + bus_risk).
    decay    = u.attrition * (1 + bus_risk)
    # Activity decays exponentially.
    v.Activity = max(0, u.Activity - dt * u.Activity * decay)
    for p in ('Devs','truck_factor','attrition'):
      setattr(v, p, getattr(u, p))

  def y(out): return out[-1][1].Activity   # reward sustained Activity

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("low truck_factor accelerates abandonment",
                   y(run({**bi, 'truck_factor':[8,1,20,'devs']}, step)),   # healthy
                   y(run({**bi, 'truck_factor':[1,1,20,'devs']}, step)),   # one-person
                   'down')
  return Model(init, step, y, rq, 'truck_factor')


def deprot():
  """Decan, Mens, Constantinou (2018) "On the impact of security
  vulnerabilities in the npm package dependency network." Stale deps
  accumulate CVE exposure: each unpatched version-pin is a sitting
  target until either updated or disclosed.

  Stocks (UPPER):
    Deps  : total dependency count declared by the project
    Stale : subset of Deps whose pinned version is below latest available
    Vulns : cumulative vulnerability surface (count of CVE-exposed deps)
  Params (lower):
    update_rate         : fraction of Stale moved to fresh per timestep
                          (the project's policy lever)
    vuln_disclose_rate  : background rate at which Stale deps gain CVEs
                          (set by the world, not the project)

  Thesis: lowering update_rate from 0.30 to 0.02 (15x slower) inflates
  terminal Vulns. CONFIRM expected for any non-trivial disclose rate."""
  init = {'Deps':[40,1,500,'deps'],                 # 40 deps is typical mid-size Java/Python
          'Stale':[20,0,500,'deps'],                # half stale at t=0 is the project's debt
          'Vulns':[0,0,500,'cves'],                 # no exposure at t=0
          'update_rate':[0.1,0,1,'frac/tick'],           # *** ctrl ***; 10% Stale renewed per tick
          'vuln_disclose_rate':[0.01,0,0.5,'frac/tick']} # 1% Stale gets a CVE per tick

  def step(dt, t, u, v):
    # Flow OUT of Stale: project actively updates that fraction this tick.
    fresh_flow = u.Stale * u.update_rate
    # Flow INTO Vulns: world discloses CVEs against Stale deps.
    new_vuln   = u.Stale * u.vuln_disclose_rate
    # Stale level: drift IN at 5% of total Deps (entropy — deps age constantly),
    # drift OUT at fresh_flow. Floor at 0 to prevent negative stock under
    # high update_rate.
    v.Stale = max(0, u.Stale + dt * (u.Deps * 0.05 - fresh_flow))
    # Vulnerability count integrates the disclosure flow; only grows.
    v.Vulns = u.Vulns + dt * new_vuln
    # Hold params + Deps constant across the run (steady-state input).
    for p in ('Deps','update_rate','vuln_disclose_rate'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Health metric: lower Vulns = better. Negate so higher y = better.
    return -out[-1][1].Vulns

  def rq(bg=None):
    # rq fires once at the high (defensive) update_rate, once at the low
    # (negligent) update_rate. Thesis claims low rate hurts -> 'down'.
    bi = init if bg is None else bg
    return verdict("low update_rate inflates vulnerabilities",
                   y(run({**bi, 'update_rate':[0.30,0,1,'frac/tick']}, step)),  # defensive
                   y(run({**bi, 'update_rate':[0.02,0,1,'frac/tick']}, step)),  # negligent
                   'down')

  return Model(init, step, y, rq, 'update_rate')


def scope():
  """Boehm (1981 Software Eng. Economics) + Jones (Applied Software
  Measurement, 2008) on scope creep. The workhorse failure mode:
  requirement inflow exceeds delivery outflow, backlog grows
  unbounded, calendar slips.

  Stocks (UPPER):
    Backlog : requirements not yet delivered
    Done    : delivered features
  Params (lower):
    inflow  : new requirements arriving per tick (the world)
    outflow : team's delivery capacity per tick (the team)

  Thesis: tripling inflow (5 -> 15) without changing outflow drops
  net Done (delivered - 10% of Backlog penalty)."""
  init = {'Backlog':[100,0,10000,'items'],      # 100 items already piled up
          'Done':[0,0,10000,'items'],           # nothing delivered yet
          'inflow':[8,0,100,'items/tick'],           # *** ctrl ***; 8 items arrive/tick
          'outflow':[6,0,100,'items/tick']}          # 6 items delivered/tick (chronic deficit)

  def step(dt, t, u, v):
    # Can only serve what exists in the Backlog, up to outflow capacity.
    served = min(u.Backlog, u.outflow)
    # Backlog rises by (inflow - served). Negative when team catches up.
    v.Backlog = u.Backlog + dt * (u.inflow - served)
    # Done strictly grows.
    v.Done    = u.Done    + dt * served
    for p in ('inflow','outflow'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Reward Done minus 10% of remaining Backlog (visible unfinished work).
    return out[-1][1].Done - out[-1][1].Backlog * 0.1

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("inflow >> outflow drowns Done",
                   y(run({**bi, 'inflow':[5,0,100,'items/tick']},  step)),    # under-capacity
                   y(run({**bi, 'inflow':[15,0,100,'items/tick']}, step)),    # creep
                   'down')
  return Model(init, step, y, rq, 'inflow')


def ctxswitch():
  """Weinberg (Quality Software Management, 1992) + Meyer, Fritz,
  Murphy, Zimmermann (2014 FSE "developers' perceptions of
  productivity"). Per-developer context-switching costs ramp-up
  time; cost scales roughly linearly with the count of distinct
  modules each dev touches per day.

  Stocks (UPPER):
    Devs : developer count
    Done : cumulative delivered work
  Params (lower):
    work_per_dev : baseline items/dev/tick when focused
    diversity    : files touched per dev per day (1 = focused, 20 = chaos)

  Thesis: quadrupling diversity (2 -> 8) hurts Done. Effective
  productivity = work_per_dev / (1 + 0.4 * (diversity - 1)). Weinberg's
  0.4 coefficient says 1 extra file ~40% productivity hit."""
  init = {'Devs':[10,1,200,'devs'],            # 10 devs
          'Done':[0,0,10000,'items'],           # nothing delivered yet
          'work_per_dev':[10,0,50,'items/dev/tick'],     # 10 items/dev/tick focused
          'diversity':[2,1,20,'files/dev/day']}         # *** ctrl ***; 2 files/dev/day default

  def step(dt, t, u, v):
    # Effective per-dev throughput drops with diversity:
    #   eff = work_per_dev / (1 + 0.4*(diversity-1))
    # diversity=1 -> eff = work_per_dev (no penalty)
    # diversity=8 -> eff = work_per_dev / 3.8 (~73% drop)
    eff = u.work_per_dev / (1 + 0.4 * (u.diversity - 1))
    v.Done = u.Done + dt * u.Devs * eff
    for p in ('Devs','work_per_dev','diversity'):
      setattr(v, p, getattr(u, p))

  def y(out): return out[-1][1].Done   # reward total Done

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("high file-diversity per dev hurts throughput",
                   y(run({**bi, 'diversity':[2,1,20,'files/dev/day']}, step)),    # focused
                   y(run({**bi, 'diversity':[8,1,20,'files/dev/day']}, step)),    # chaotic
                   'down')
  return Model(init, step, y, rq, 'diversity')


def limits():
  """Senge (1990) "The Fifth Discipline" limits-to-growth archetype.
  Effort produces linear gains until a saturating constraint bites
  (coordination overhead, infra capacity, market). Past the knee,
  doubling input yields diminishing returns.

  Stocks (UPPER):
    Devs : team size (held constant per run)
    Done : cumulative delivered work
  Params (lower):
    k_per_dev : raw productivity coefficient (items/dev/tick)
    cap       : structural ceiling on per-tick output (hyperbolic saturation)

  Thesis: doubling Devs near cap (30 -> 60) yields LESS than 2x Done.
  Tested with expect='up' — if the model is right we expect SOME
  gain, but the verdict checks the gap is smaller than linear."""
  init = {'Devs':[10,1,500,'devs'],            # *** ctrl ***; 10 devs default
          'Done':[0,0,1e5,'items'],             # nothing delivered yet
          'k_per_dev':[10,0,100,'items/dev/tick'],       # 10 items/dev/tick raw
          'cap':[200,10,1000,'items/tick']}          # saturate at 200 items/tick

  def step(dt, t, u, v):
    # Raw demand: linear in team size.
    raw = u.Devs * u.k_per_dev
    # Hyperbolic saturation: eff = raw / (1 + raw/cap).
    # Below knee (raw << cap) eff ~ raw. Near cap, eff ~ cap.
    eff = raw / (1 + raw / max(1, u.cap))
    v.Done = u.Done + dt * eff
    for p in ('Devs','k_per_dev','cap'):
      setattr(v, p, getattr(u, p))

  def y(out): return out[-1][1].Done   # reward total Done

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("doubling Devs near cap yields diminishing returns",
                   y(run({**bi, 'Devs':[30,1,500,'devs']}, step)),    # near knee
                   y(run({**bi, 'Devs':[60,1,500,'devs']}, step)),    # past knee
                   'up')                                       # expect up but small
  return Model(init, step, y, rq, 'Devs')


def successful():
  """Merton (1968 Science) "The Matthew Effect in Science." Attention
  concentrates on entities that already have it: famous modules
  attract more PRs, more reviews, more tests; obscure modules atrophy.
  Small initial differences compound.

  Stocks (UPPER):
    Pop      : total population of modules
    Attended : subset receiving active attention
    Coverage : cumulative attention units delivered
  Params (lower):
    concentration   : fraction of attention going to Attended subset (policy)
    attention_rate  : total attention budget per tick

  Thesis: pushing concentration from 0.4 (balanced) to 0.9 (extreme)
  starves the unattended set faster than the attended set gains; net
  Coverage drops."""
  init = {'Pop':[50,1,500,'modules'],              # 50 modules total
          'Attended':[10,0,500,'modules'],         # 10 currently attended (20% Pareto-ish)
          'Coverage':[0,0,1e5,'attention-units'],          # no coverage yet
          'concentration':[0.5,0,1,'frac'],     # *** ctrl ***; 50% to attended default
          'attention_rate':[3,0,30,'attention/tick']}     # 3 units/tick total budget

  def step(dt, t, u, v):
    # Attention split: concentration goes to Attended, rest to Pop.
    flow_attn = u.attention_rate * u.concentration
    flow_pop  = u.attention_rate * (1 - u.concentration)
    # Gain term: per-module attention summed across Attended and rest-of-Pop.
    gain      = u.Attended * flow_attn + (u.Pop - u.Attended) * flow_pop
    # Starve term: unattended modules lose half their attention share at
    # high concentration (compound starvation).
    starve    = (u.Pop - u.Attended) * u.concentration * 0.5
    v.Coverage = u.Coverage + dt * (gain - starve)
    for p in ('Pop','Attended','concentration','attention_rate'):
      setattr(v, p, getattr(u, p))

  def y(out): return out[-1][1].Coverage   # reward total Coverage

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("extreme concentration starves Coverage",
                   y(run({**bi, 'concentration':[0.4,0,1,'frac']}, step)),  # balanced
                   y(run({**bi, 'concentration':[0.9,0,1,'frac']}, step)),  # extreme
                   'down')
  return Model(init, step, y, rq, 'concentration')


def maturity():
  """Humphrey (1989) "Managing the Software Process" + Paulk et al (1993)
  Capability Maturity Model + Harter, Krishnan, Slaughter (2000 Mgmt
  Science) "Effects of process maturity on quality, cycle time, and
  effort": higher institutionalised-process maturity reduces both
  defect injection AND defect dwell-time. The Harter et al regression
  put a quantitative footing under the SEI CMM claims.

  Stocks (UPPER):
    Bugs    : outstanding defects at any moment
    BugTime : cumulative defect-time integral (sum of Bugs(t) over t)
              — a Little's-law-style 'bug-dwell' measure: low BugTime
              means defects don't sit around.
    Done    : cumulative work delivered
  Params (lower):
    work_rate     : commits per tick (constant)
    inj_rate_base : base bug-injection rate (bugs per commit) at maturity=0
    fix_rate_base : base bug-fix rate (frac of Bugs per tick) at maturity=0
    maturity      : process maturity in [0,1] mapping loosely to CMMI
                    levels 1-5; the ctrl lever (policy).

  Effects of maturity:
    - injection scales by (1 - 0.7*maturity)  : higher maturity injects fewer
    - fix      scales by (1 + 1.5*maturity)  : higher maturity fixes faster
  Combined: BugTime drops as maturity rises.

  Thesis: raising maturity from 0.1 (CMMI L1 chaos) to 0.9 (CMMI L5
  optimising) sharply reduces total BugTime."""
  init = {'Bugs':[10,0,500,'bugs'],                  # 10 outstanding at t=0
          'BugTime':[0,0,1e5,'bug-ticks'],            # nothing accumulated yet
          'Done':[0,0,5000,'items'],                  # no delivery yet
          'work_rate':[10,0,100,'items/tick'],        # 10 commits/tick base
          'inj_rate_base':[0.5,0,3,'bugs/item'],      # base 0.5 bugs/commit
          'fix_rate_base':[0.05,0,1,'frac/tick'],     # 5% Bugs fixed/tick base
          'maturity':[0.3,0,1,'frac']}                # *** ctrl ***; CMMI L2-3 default

  def step(dt, t, u, v):
    # Injection: base rate, lowered by maturity (up to 70% reduction).
    bugs_in = u.work_rate * u.inj_rate_base * (1 - 0.7 * u.maturity)
    # Fixing: base rate, raised by maturity (up to 2.5x).
    fix_eff = u.fix_rate_base * (1 + 1.5 * u.maturity)
    bugs_out = u.Bugs * fix_eff
    # Bug stock: net of injection and fixing. Floor at 0.
    v.Bugs    = max(0, u.Bugs + dt * (bugs_in - bugs_out))
    # Bug-time integral: tracks dwell. Higher = bugs lived longer in
    # the system. Like person-days but for defects.
    v.BugTime = u.BugTime + dt * u.Bugs
    # Delivered work; mature processes don't ship faster directly, but
    # spend less time on rework — track for context.
    v.Done    = u.Done    + dt * u.work_rate
    for p in ('work_rate','inj_rate_base','fix_rate_base','maturity'):
      setattr(v, p, getattr(u, p))

  def y(out):
    # Health: low BugTime is the prize. Negate so higher y = better.
    return -out[-1][1].BugTime

  def rq(bg=None):
    bi = init if bg is None else bg
    return verdict("higher maturity reduces total BugTime",
                   y(run({**bi, 'maturity':[0.9,0,1,'frac']}, step)),  # CMMI L5
                   y(run({**bi, 'maturity':[0.1,0,1,'frac']}, step)),  # CMMI L1
                   'down')
  return Model(init, step, y, rq, 'maturity')


ALL_MODELS = [diapers, brooks, bugs, debt, sir, rework, learn, brooksq,
              defmap, aiwork, flaky, dora, micro, teamtopo, burnout, aidebt,
              archpat, congruence,
              # 15 added 2026-05-25 from docs/other.html buildable-today list:
              little, coordn2, entropy, costchange, pareto, linus, mirroring,
              orgchurn, ownership, ossfail, deprot, scope, ctxswitch, limits,
              successful,
              # 1 added 2026-05-26 per domain-expert request:
              maturity]


def main():
  print(f"{'model':<10} {'verdict':<8} {'y0':>10} {'y1':>10} {'gap':>10}")
  print("-" * 60)
  for f in ALL_MODELS:
    m = f()
    r = m.rq()
    print(f"{f.__name__:<10} {r['verdict']:<8} {r['y0']:>10.2f} "
          f"{r['y1']:>10.2f} {r['gap']:>+10.2f}")

if __name__ == "__main__":
  main()
