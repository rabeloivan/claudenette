# A regular package, not an implicit namespace one. Python gives a regular
# package named `tests` found anywhere on sys.path precedence over a
# namespace directory found earlier - and some pip packages leave a stray
# top-level `tests` package in site-packages. With one installed, every
# module failed to load ("Could not load configuration for 'C00'") although
# its files were all there.
