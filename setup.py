from setuptools import setup, Extension
import os
import sys
import platform

#dbf = open('/tmp/build.log', 'w')
#def mprint(s):
#    print(s, file=dbf)
mprint=lambda *_: None

def get_pgplot_library_config():
    libraries = []
    library_dirs = []
    runtime_library_dirs = []
    extra_link_args = []
    include_dirs = []
    
    if os.name != "posix":
        raise Exception("OS not supported")
        
    # Base libraries needed on POSIX systems
    libraries.extend(["X11", "m"])
    
    # Standard X11 library locations
    for ld in filter(os.path.isdir, ["/usr/lib/x86_64-linux-gnu/", "/usr/X11R6/lib/", "/opt/X11/lib"]):
        library_dirs.append(ld)
    
    # Handle PGPLOT/Giza configuration
    soext = 'dylib' if platform.system() == 'Darwin' else 'so'
    pgplotdir = os.environ.get("PGPLOT_DIR")
    
    if pgplotdir:
        if not os.path.isdir(pgplotdir):
            raise RuntimeError(f"$PGPLOT_DIR [{pgplotdir}] is not a directory")
            
        # Find libcpgplot
        for path, _, files in os.walk(pgplotdir):
            mprint(f"Inspecting files {files}")
            if f'libcpgplot.{soext}' in files:
                mprint(f" => found libcpgplot.{soext}")
                # Configure library paths and linking
                if platform.system() != 'Darwin':
                    extra_link_args.append(f"-Wl,-rpath={path}")
                    mprint(" adding '-Wl,-rpath={path}'")
                else:
                    extra_link_args.append(f"-Wl,-rpath,{path}")
                    mprint(" adding '-Wl,-rpath,{path}'")

                extra_link_args.extend([
                    os.path.join(path, f"libcpgplot.{soext}"),
                    os.path.join(path, f"libpgplot.{soext}")
                ])
                runtime_library_dirs.append(path)
                include_dirs.append(os.path.join(pgplotdir, "include"))
                break
        else:
            raise RuntimeError(f"Could not find libcpgplot in $PGPLOT_DIR [{pgplotdir}]")
    # MacOS X SCISOFT support
    elif 'SCIDIR' in os.environ:
        libraries.append("aquaterm")
        library_dirs.append(os.path.join(os.environ["SCIDIR"], 'lib'))
    else:
        print("PGPLOT_DIR env var not defined, hoping libcpgplot is in system path(s)", file=sys.stderr)
        libraries.extend(["cpgplot", "pgplot"])

    mprint(f"DONE:\n\tlibraries={libraries}\n\tlibrary_dirs={library_dirs}\n\textra_link_args={extra_link_args}\n\tinclude_dirs={include_dirs}")
    
    return {
        'libraries': libraries,
        'library_dirs': library_dirs,
        'runtime_library_dirs': runtime_library_dirs,
        'extra_link_args': extra_link_args,
        'include_dirs': include_dirs
    }

def get_extension_config():
    try:
        import numpy
        include_dirs = [numpy.get_include()]
        define_macros = [('USE_NUMPY', None), ('NPY_NO_DEPRECATED_API',  'NPY_1_7_API_VERSION')]
        undef_macros = ['USE_NUMARRAY']
    except ImportError:
        raise Exception("numpy is required for building ppgplot")
    
    pgplot_config = get_pgplot_library_config()
    include_dirs.extend(pgplot_config['include_dirs'])
    
    return Extension('ppgplot._ppgplot',
                    sources=[os.path.join('src', '_ppgplot.c')],
                    include_dirs=include_dirs,
                    libraries=pgplot_config['libraries'],
                    library_dirs=pgplot_config['library_dirs'],
                    runtime_library_dirs=pgplot_config['runtime_library_dirs'],
                    extra_link_args=pgplot_config['extra_link_args'],
                    define_macros=define_macros,
                    undef_macros=undef_macros)
setup(
        ext_modules=[
            get_extension_config(),
        ]
)

#setup(
#    ext_modules=[
#        Extension(
#            name="ppgplot",
#            sources=["src/_ppgplot.c"],
#        ),
#    ]
#)
#
#import os
#import sys
#import platform
#
#def get_pgplot_library_config():
#    libraries = []
#    library_dirs = []
#    runtime_library_dirs = []
#    extra_link_args = []
#    include_dirs = []
#    
#    if os.name != "posix":
#        raise Exception("OS not supported")
#        
#    # Base libraries needed on POSIX systems
#    libraries.extend(["X11", "m"])
#    
#    # Standard X11 library locations
#    for ld in filter(os.path.isdir, ["/usr/lib/x86_64-linux-gnu/", "/usr/X11R6/lib/", "/opt/X11/lib"]):
#        library_dirs.append(ld)
#    
#    # Handle PGPLOT/Giza configuration
#    soext = 'dylib' if platform.system() == 'Darwin' else 'so'
#    pgplotdir = os.environ.get("PGPLOT_DIR")
#    
#    if pgplotdir:
#        if not os.path.isdir(pgplotdir):
#            raise RuntimeError(f"$PGPLOT_DIR [{pgplotdir}] is not a directory")
#            
#        # Find libcpgplot
#        for path, _, files in os.walk(pgplotdir):
#            if f'libcpgplot.{soext}' in files:
#                # Configure library paths and linking
#                if platform.system() != 'Darwin':
#                    extra_link_args.append(f"-Wl,-rpath={path}")
#                extra_link_args.extend([
#                    os.path.join(path, f"libcpgplot.{soext}"),
#                    os.path.join(path, f"libpgplot.{soext}")
#                ])
#                runtime_library_dirs.append(path)
#                include_dirs.append(os.path.join(pgplotdir, "include"))
#                break
#        else:
#            raise RuntimeError(f"Could not find libcpgplot in $PGPLOT_DIR [{pgplotdir}]")
#    
#    # MacOS X SCISOFT support
#    elif 'SCIDIR' in os.environ:
#        libraries.append("aquaterm")
#        library_dirs.append(os.path.join(os.environ["SCIDIR"], 'lib'))
#    else:
#        print("PGPLOT_DIR env var not defined, hoping libcpgplot is in system path(s)", file=sys.stderr)
#        libraries.extend(["cpgplot", "pgplot"])
#    
#    return {
#        'libraries': libraries,
#        'library_dirs': library_dirs,
#        'runtime_library_dirs': runtime_library_dirs,
#        'extra_link_args': extra_link_args,
#        'include_dirs': include_dirs
#    }
#
#def get_extension_config():
#    try:
#        import numpy
#        include_dirs = [numpy.get_include()]
#        define_macros = [('USE_NUMPY', None)]
#        undef_macros = ['USE_NUMARRAY']
#    except ImportError:
#        raise Exception("numpy is required for building ppgplot")
#    
#    pgplot_config = get_pgplot_library_config()
#    include_dirs.extend(pgplot_config['include_dirs'])
#    
#    return Extension('ppgplot._ppgplot',
#                    sources=[os.path.join('src', '_ppgplot.c')],
#                    include_dirs=include_dirs,
#                    libraries=pgplot_config['libraries'],
#                    library_dirs=pgplot_config['library_dirs'],
#                    runtime_library_dirs=pgplot_config['runtime_library_dirs'],
#                    extra_link_args=pgplot_config['extra_link_args'],
#                    define_macros=define_macros,
#                    undef_macros=undef_macros)
#
#if __name__ == '__main__':
#    setup(
#        name="ppgplot",
#        version="1.4",
#        description="Python / Numeric-Python bindings for PGPLOT",
#        author="Nick Patavalis",
#        author_email="npat@efault.net",
#        url="http://code.google.com/p/ppgplot/ https://github.com/haavee/ppgplot",
#        packages=["ppgplot"],
#        package_dir={"ppgplot": "src"},
#        ext_modules=[get_extension_config()]
#    )
