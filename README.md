# ppgplot

ppgplot - The Pythonic interface to PGPLOT, with support for both PGPLOT and Giza backends.

`ppgplot` is a python module (extension) providing bindings to the PGPLOT
graphics library. PGPLOT is a scientific visualization (graphics) library
written in Fortran by T. J. Pearson. C bindings for PGPLOT are also available.
`ppgplot` makes the library usable by Python programs. It had support for the Numeric /
numarray modules, but nowadays (>= Feb 2025) replaced by Numpy, to efficiently represent and
manipulate vectors and matrices.

Currently, as the extension is not in PyPI, you're installing it into an "externally managed environment". You may need to create a Python [`venv`](https://docs.python.org/3/library/venv.html) first in order to install the extension manually on your system.


## Requirements

- Python 3.7+
- numpy >= 1.21.0
- PGPLOT or Giza libraries installed
- X11 development libraries
- pkg-config 

### Installing the dependencies

On Linux use your favourite package manager, e.g.:
```bash
$> sudo apt-get install giza-dev libx11-dev pkg-config
```

Successful installation using [Homebrew](https://brew.sh) on Mac OSX with:
```bash
$> brew install libx11 giza pkgconf
```

## Installation

In principle, this extension should build out-of-the-box in a Python `venv`, or, if you have it, a `conda` virtual environment (untested at the moment).
The [`pyproject.toml`](pyproject.toml) file lists all dependencies and should (...) pull them into the `venv` as required for building/deploying:

```bash
$> cd /path/to/checkout/of/this/repo
$> pip install [-e] .
```

Without `-e` installs the extension in the `venv`, with the `-e` keeps the module in the current directory.


## Using a bespoke PGPLOT or Giza backend

The extension configuration allows compiling + linking to a locally compiled [PGPLOT](https://sites.astro.caltech.edu/~tjp/pgplot/) or [Giza](https://github.com/danieljprice/giza) library.


Obviously, first install or build PGPLOT and/or Giza on your system (should you want to compare them).
Then build the extension, pointing the `PGPLOT_DIR` environment variable to the installation directory of the backend of choice:

```bash
$> PGPLOT_DIR=/path/to/pgplot pip install [-e] . 
```

## Notes

FORTRAN? Srsly? Actually, for plotting large numbers of points or simple, yet precise control of the graphics, the FORTRAN based PGPLOT backend is convenient and _fast_ (a _lot_ faster than `matplotlib`, and still noticeably faster than `Giza`). However, the upside of investing those compute cycles is that the (anti-aliased!) fonts and graphics produced by the [`cairo`](https://www.cairographics.org) library (the _actual_ graphics backend used by `Giza`) are of an amazing quality.

If `ppgplot` is linked against the `Giza` library, it can produce output in `.png` and `.pdf`, also not something to be sneezed at.

All in all, the `Giza` backend is an amazing job done, but it is [not 100% compatible with the original PGPLOT](https://danieljprice.github.io/giza/documentation/pgplot.html), so it is not guaranteed your plots will come out identical.

This fork of the Python-extension owes a lot of thanks to the original author of `ppgplot`:
  https://github.com/npat-efault/ppgplot
