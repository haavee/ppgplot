from setuptools import setup, Extension
import os
import sys
import platform
# these deps are listed in pyproject.toml so should be able to import w/o probs
import numpy
import pkgconfig


def add_pgplot_from_giza(ext):
    # Very convenient
    pkgconfig.configure_extension(ext, 'giza', static=True)
    # But not sufficient ...
    ext.libraries.extend( ['cpgplot', 'pgplot'] )
    return ext

# Configure the Extension based on stuff found in PGPLOT_DIR
def add_pgplot_from_pgplot_dir(ext, pgplotdir):
    if not os.path.isdir(pgplotdir):
        raise RuntimeError(f"$PGPLOT_DIR [{pgplotdir}] is not a directory")
    darwin    = 'darwin' in platform.system().lower()
    soext     = 'dylib' if darwin else 'so'
    mk_rpath  = ("-Wl,-rpath,{0}" if darwin else "-Wl,-rpath={0}").format
    mk_lib    = f"lib{{0}}.{soext}".format
    # Find libcpgplot
    lib       = mk_lib("cpgplot")
    for path, _, files in os.walk(pgplotdir):
        if lib not in files:
            continue
        # OK found it!
        # Configure runtime library paths
        ext.extra_link_args.append( mk_rpath(path) )

        # Because we're overriding system settings, add
        # the libraries with absolute path
        ext.extra_link_args.extend( map(lambda l: os.path.join(path, l),
                                        map(mk_lib, ['cpgplot', 'pgplot'])) )
        ext.runtime_library_dirs.append( path )
        ext.include_dirs.append( os.path.join(pgplotdir, "include") )
        break
    else:
        raise RuntimeError(f"Could not find libcpgplot in $PGPLOT_DIR [{pgplotdir}]")
    return ext

# Extract useful info from the numpy module
def add_numpy(ext):
    ext.include_dirs.append( numpy.get_include() )
    return ext

# Set up X11 libraries, searching standard (Linux...) paths
def add_X11(ext):
    ext.libraries.extend(['X11', 'm'])
    # Standard X11 library locations
    ext.library_dirs.extend(
            filter(os.path.isdir,
                   ["/usr/lib/x86_64-linux-gnu/", "/usr/X11R6/lib/", "/opt/X11/lib"])
    )
    return ext


# This is the main Extension configuration step
# We go over the dependencies, each of which
# can modify the build env as needed
def set_extension_config(ext):
    # yah ... maybe later if we grow up widen this
    if os.name != "posix":
        raise Exception("OS not supported")

    # modify the extension to taste
    add_X11(ext)
    add_numpy(ext)

    # Where to source pgplot from
    pgplot_dir = os.environ.get('PGPLOT_DIR', None)
    if pgplot_dir is not None:
        add_pgplot_from_pgplot_dir(ext, pgplot_dir)
    else:
        add_pgplot_from_giza(ext)
    return ext

###########################################################
#             This triggers the whole build               #
###########################################################
setup(
        ext_modules=[
            set_extension_config( Extension('ppgplot._ppgplot',
                                            sources=[os.path.join('src', '_ppgplot.c')]) ),
        ]
)

