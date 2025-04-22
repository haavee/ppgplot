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

def print_config(ext):
    print("===> Extension contents")
    print(f"\tname = {ext.name}")
    print(f"\tsources = {ext.sources}")
    print(f"\tlibraries = {ext.libraries}")
    print(f"\tdefine_macros = {ext.define_macros}")
    print(f"\tundef_macros = {ext.undef_macros}")
    print(f"\tlibrary_dirs = {ext.library_dirs}")
    print(f"\tinclude_dirs = {ext.include_dirs}")
    print(f"\textra_link_args = {ext.extra_link_args}")
    print(f"\truntime_library_dirs = {ext.runtime_library_dirs}")
    print(f"\textra_objects = {ext.extra_objects}")
    print(f"\textra_compile_args = {ext.extra_compile_args}")
    print(f"\texport_symbols = {ext.export_symbols}")
    print(f"\tswig_opts = {ext.swig_opts}")
    print(f"\tdepends = {ext.depends}")
    print(f"\tlanguage = {ext.language}")
    print(f"\toptional = {ext.optional}")
    print(f"\tpy_limited_api = {ext.py_limited_api}")
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
        name="python-pgplot",
        ext_modules=[
            set_extension_config( Extension('ppgplot._ppgplot',
                                            sources=[os.path.join('src', '_ppgplot.c')]) ),
        ]
)

