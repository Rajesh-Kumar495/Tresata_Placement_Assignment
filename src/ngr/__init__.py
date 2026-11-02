"""Non-GAAP earnings-release review assistant (prototype).

Layering (see docs/design/architecture.md):
  numeric, docmodel, tieout  -> deterministic, no I/O, no randomness
  labels                     -> gold-label schema + validator (eval-first)
  config, edgar              -> environment + EDGAR access (network)
"""

__version__ = "0.1.0"
