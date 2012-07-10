from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
import sys, os, re

version = '0.5'

try:
	os.stat("src")
except OSError:
	try:
		os.stat("../4store/src")
	except OSError:
		print """
Could not find 4store sources in ../4store/src

Either ensure that the 4store source distribution is in ../4store
or else make a symbolic link from its src subdirectory to the 
py4s directory.

Recommend you use the git HEAD version of 4store, available from

	git://github.com/garlik/4store.git

Or the experimental branch with support for multiple simultaneous
clients from

	git://github.com/wwaites/4store.git

and remember use the latest version of rasqal and configure it
with

	'--enable-query-languages=sparql rdql laqrs'

so as to have COUNT support.
"""
		sys.exit(1)
	os.symlink("../4store/src", "src")

def get_includes(pkg):
	fp = os.popen("pkg-config --cflags-only-I %s 2> /dev/null" % (pkg,))
	includes = fp.read().strip().replace("-I", "").split(" ")
	fp.close()
	return includes
def get_libs(pkg):
	fp = os.popen("pkg-config --libs-only-L %s 2> /dev/null" % (pkg,))
	libdirs = fp.read().strip().replace("-L", "").split(" ")
	fp.close()
	fp = os.popen("pkg-config --libs-only-l %s 2> /dev/null" % (pkg,))
	libs = fp.read().strip().replace("-l", "").split(" ")
	fp.close()
	return libdirs, libs
def uniqify(l):
	seen = []
	for e in l:
		if not e or e in seen: continue
		seen.append(e)
	return seen
extra_includes = get_includes("glib-2.0") + get_includes("raptor") + get_includes("rasqal")
extra_includes = uniqify(extra_includes)
glib_dirs, glib_libs = get_libs("glib-2.0")
raptor_dirs, raptor_libs = get_libs("raptor")
rasqal_dirs, rasqal_libs = get_libs("rasqal")
avahi_client_dirs, avahi_client_libs = get_libs("avahi-client")
avahi_glib_dirs, avahi_glib_libs = get_libs("avahi-glib")
library_dirs = uniqify(glib_dirs + rasqal_dirs + raptor_dirs + avahi_client_dirs + avahi_glib_dirs)
libraries = uniqify(glib_libs + rasqal_libs + raptor_libs + avahi_client_libs + avahi_glib_libs)

define_macros=[]
define_macros.append(("FS_BIN_DIR", "\"/usr/local/bin\""))

if not os.system("pkg-config rasqal --atleast-version=0.9.14"):
	define_macros.append(("HAVE_LAQRS", 1))
if not os.system("pkg-config rasqal --atleast-version=0.9.16"):
	define_macros.append(("HAVE_RASQAL_WORLD", 1))
if not os.system("pkg-config --exists avahi-client avahi-glib"):
	define_macros.append(("USE_AVAHI", 1))
else:
	try:
		os.stat("/usr/include/dns_sd.h")
		define_macros.append(("USE_DNS_SD", 1))
	except OSError:
		pass

_rev = os.popen("git describe --tags 2> /dev/null").read().strip()
if _rev:
	version = _rev
else:
	_rev = os.popen("git describe --always --tags 2> /dev/null").read().strip()
	if _rev:
		version = _rev

libpy4s = Extension(
        name="_py4s",
        sources=[
		"_py4s.pyx",
		"src/common/4s-common.c",
		"src/common/4s-client.c",
		"src/common/4s-mdns.c",
        "src/admin/admin_common.c",
        "src/admin/admin_frontend.c",
        "src/admin/admin_protocol.c",
        "src/common/bit_arr.c",
		"src/common/datatypes.c",
		"src/common/error.c",
		"src/common/umac.c",
		"src/common/rijndael-alg-fst.c",
		"src/common/md5.c",
		"src/common/hash.c",
		"src/common/msort.c",
		"src/common/qsort.c",
		"src/frontend/query.c",
		"src/frontend/query-cache.c",
		"src/frontend/query-datatypes.c",
		"src/frontend/filter.c",
		"src/frontend/filter-datatypes.c",
		"src/frontend/decimal.c",
		"src/frontend/results.c",
		"src/frontend/optimiser.c",
		"src/frontend/query-data.c",
		"src/frontend/order.c",
		"src/frontend/import.c",
		"src/frontend/update.c",
                "src/frontend/group.c",
		"py4s_helpers.c",
                "src/libs/stemmer/runtime/utilities.c",
                "src/libs/double-metaphone/double_metaphone.c",
                "src/libs/stemmer/runtime/api.c",
                "src/libs/mt19937-64/mt19937-64.c",
                "src/libs/stemmer/libstemmer/libstemmer.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_danish.c",
                "src/libs/stemmer/src_c/stem_UTF_8_danish.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_dutch.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_english.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_finnish.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_french.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_german.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_hungarian.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_italian.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_norwegian.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_porter.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_portuguese.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_spanish.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_1_swedish.c",
                "src/libs/stemmer/src_c/stem_ISO_8859_2_romanian.c",
                "src/libs/stemmer/src_c/stem_KOI8_R_russian.c",
                "src/libs/stemmer/src_c/stem_UTF_8_dutch.c",
                "src/libs/stemmer/src_c/stem_UTF_8_english.c",
                "src/libs/stemmer/src_c/stem_UTF_8_finnish.c",
                "src/libs/stemmer/src_c/stem_UTF_8_french.c",
                "src/libs/stemmer/src_c/stem_UTF_8_german.c",
                "src/libs/stemmer/src_c/stem_UTF_8_hungarian.c",
                "src/libs/stemmer/src_c/stem_UTF_8_italian.c",
                "src/libs/stemmer/src_c/stem_UTF_8_norwegian.c",
                "src/libs/stemmer/src_c/stem_UTF_8_porter.c",
                "src/libs/stemmer/src_c/stem_UTF_8_portuguese.c",
                "src/libs/stemmer/src_c/stem_UTF_8_romanian.c",
                "src/libs/stemmer/src_c/stem_UTF_8_russian.c",
                "src/libs/stemmer/src_c/stem_UTF_8_spanish.c",
                "src/libs/stemmer/src_c/stem_UTF_8_swedish.c",
                "src/libs/stemmer/src_c/stem_UTF_8_turkish.c"

	],
	extra_compile_args=["-std=gnu99"],
        define_macros=define_macros,
	include_dirs=["src"] + extra_includes,
	library_dirs=library_dirs,
 	libraries=["pcre"] + libraries,
)

setup(name='py4s',
	version=version,
	description="Python C bindings for 4store",
	long_description="""\
Python C bindings for 4store""",
	classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
	keywords='4store rdf triplestore',
	author='William Waites',
	author_email='wwaites_at_gmail.com',
	url='http://github.com/wwaites/py4s',
	license='GPL',
	packages=["py4s"],
	cmdclass={'build_ext': build_ext},
	ext_modules=[libpy4s],
)
