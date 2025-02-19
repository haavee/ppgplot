from setuptools import setup, Extension
import os
import sys
import platform
import operator
# these deps are listed in pyproject.toml so should be able to import w/o probs
import numpy
import pkgconfig


def add_pgplot_from_giza(ext):
    # Very convenient - but also breaks the build on Linux (Deb12) *sigh*
    # adds an empty string [''] to ext.extra_compile_args
    pkgconfig.configure_extension(ext, 'giza', static=True)
    ext.extra_compile_args = list( filter(operator.truth, ext.extra_compile_args) )
    # But not sufficient ...
    ext.libraries.extend( ['cpgplot', 'pgplot'] )
    return ext

# Configure the Extension based on stuff found in PGPLOT_DIR
def add_pgplot_from_pgplot_dir(ext, pgplotdir):
    if not os.path.isdir(pgplotdir):
        raise RuntimeError("$PGPLOT_DIR [{0}] is not a directory".format(pgplotdir))
    darwin    = 'darwin' in platform.system().lower()
    soext     = 'dylib' if darwin else 'so'
    mk_rpath  = ("-Wl,-rpath,{0}" if darwin else "-Wl,-rpath={0}").format
    mk_lib    = "lib{{0}}.{0}".format(soext).format
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
        raise RuntimeError("Could not find libcpgplot in $PGPLOT_DIR [{0}]".format(pgplotdir))
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

def print_config(ext):
    print("===> Extension contents")
    print("\tname = {ext.name}", **locals())
    print("\tsources = {ext.sources}", **locals())
    print("\tlibraries = {ext.libraries}", **locals())
    print("\tdefine_macros = {ext.define_macros}", **locals())
    print("\tundef_macros = {ext.undef_macros}", **locals())
    print("\tlibrary_dirs = {ext.library_dirs}", **locals())
    print("\tinclude_dirs = {ext.include_dirs}", **locals())
    print("\textra_link_args = {ext.extra_link_args}", **locals())
    print("\truntime_library_dirs = {ext.runtime_library_dirs}", **locals())
    print("\textra_objects = {ext.extra_objects}", **locals())
    print("\textra_compile_args = {ext.extra_compile_args}", **locals())
    print("\texport_symbols = {ext.export_symbols}", **locals())
    print("\tswig_opts = {ext.swig_opts}", **locals())
    print("\tdepends = {ext.depends}", **locals())
    print("\tlanguage = {ext.language}", **locals())
    print("\toptional = {ext.optional}", **locals())
    print("\tpy_limited_api = {ext.py_limited_api}", **locals())
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
    # uncomment and run "pip -v install [-e] ." to see output
    #print_config(ext)
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

