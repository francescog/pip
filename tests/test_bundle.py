
import zipfile
import textwrap
from os.path import abspath, join, dirname, pardir
from test_pip import here, reset_env, run_pip, pyversion, write_file #, lib_py
from path import Path

def test_create_bundle():
    """
    Test making a bundle.  We'll grab one package from the filesystem
    (the FSPkg dummy package), one from vcs (initools) and one from an
    index (pip itself).

    """
    env = reset_env()
    fspkg = 'file://%s/FSPkg' % join(here, 'packages')
    dummy = run_pip('install', '-e', fspkg)
    pkg_lines = textwrap.dedent('''\
            -e %s
            -e svn+http://svn.colorstudy.com/INITools/trunk#egg=initools-dev
            pip''' % fspkg)
    write_file('bundle-req.txt', pkg_lines)
    # Create a bundle in env.base_path/ test.pybundle
    result = run_pip('bundle', '-r', env.base_path/ 'bundle-req.txt', env.base_path/ 'test.pybundle')
    bundle = result.files_after.get('test.pybundle', None)
    from pprint import pprint
    pprint(result.files_after)
    assert bundle is not None

    files = zipfile.ZipFile(bundle.full).namelist()
    assert 'src/FSPkg/' in files
    assert 'src/initools/' in files
    assert 'build/pip/' in files
