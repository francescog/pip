
import textwrap
from os.path import join
from tempfile import mkdtemp
from test_pip import here, reset_env, run_pip, get_env, diff_states, write_file

#site_pkg = join(lib_py, 'site-packages')
#easy_install_pth = join(site_pkg, 'easy-install.pth')

def test_simple_uninstall():
    """
    Test simple install and uninstall.
    
    """
    env = reset_env()
    result = run_pip('install', 'INITools==0.2', expect_error=True)
    assert join(env.site_packages, 'initools') in result.files_created, sorted(result.files_created.keys())
    result2 = run_pip('uninstall', 'INITools', '-y', expect_error=True)
    assert diff_states(result.files_before, result2.files_after, ignore=['env/build', 'cache']).values() == [{}, {}, {}]

def test_uninstall_with_scripts():
    """
    Uninstall an easy_installed package with scripts.
    
    """
    env = reset_env()
    result = env.run('easy_install', 'PyLogo')
    easy_install_pth = env.site_packages/ 'easy-install.pth'
    assert('PyLogo' in result.files_updated[easy_install_pth].bytes), result.files_after[easy_install_pth].bytes
    result2 = run_pip('uninstall', 'pylogo', '-y', expect_error=True)
    assert diff_states(result.files_before, result2.files_after, ignore=['env/build', 'cache']).values() == [{}, {}, {}]

def test_uninstall_namespace_package():
    """
    Uninstall a distribution with a namespace package without clobbering
    the namespace and everything in it.
    
    """
    env = reset_env()
    result = run_pip('install', 'pd.requires==0.0.3', expect_error=True)
    assert join(env.site_packages, 'pd') in result.files_created, sorted(result.files_created.keys())
    result2 = run_pip('uninstall', 'pd.find', '-y', expect_error=True)
    assert join(env.site_packages, 'pd') not in result2.files_deleted, sorted(result2.files_deleted.keys())
    assert join(env.site_packages, 'pd', 'find') in result2.files_deleted, sorted(result2.files_deleted.keys())

def test_uninstall_console_scripts():
    """
    Test uninstalling a package with more files (console_script entry points, extra directories).
    
    """
    reset_env()
    result = run_pip('install', 'virtualenv', expect_error=True)
    assert ('env/bin/virtualenv') in result.files_created, sorted(result.files_created.keys())
    result2 = run_pip('uninstall', 'virtualenv', '-y', expect_error=True)
    assert diff_states(result.files_before, result2.files_after, ignore=['env/build', 'cache']).values() == [{}, {}, {}]

def test_uninstall_easy_installed_console_scripts():
    """
    Test uninstalling package with console_scripts that is easy_installed.
    
    """
    env = reset_env()
    result = env.run('easy_install', 'virtualenv')
    assert ('env/bin/virtualenv') in result.files_created, sorted(result.files_created.keys())
    result2 = run_pip('uninstall', 'virtualenv', '-y', expect_error=True)
    assert diff_states(result.files_before, result2.files_after, ignore=['env/build', 'cache']).values() == [{}, {}, {}]

def test_uninstall_editable_from_svn():
    """
    Test uninstalling an editable installation from svn.
    
    """
    env = reset_env()
    result = run_pip('install', '-e', 'svn+http://svn.colorstudy.com/INITools/trunk#egg=initools-dev', expect_error=True)
    egg_link = result.files_created[env.site_packages/ 'INITools.egg-link']
    result2 = run_pip('uninstall', '-y', 'initools', expect_error=True)
    assert ('src/initools' in result2.files_after), 'oh noes, pip deleted my sources!'
    assert diff_states(result.files_before, result2.files_after, ignore=['src/initools', 'env/build']).values() == [{}, {}, {}]

def test_uninstall_editable_with_source_outside_venv():
    """
    Test uninstalling editable install from existing source outside the venv.
    
    """
    tmpdir = join(mkdtemp(),'virtualenv')
    reset_env()
    env = get_env()
    result = env.run('hg', 'clone', 'http://bitbucket.org/ianb/virtualenv/', tmpdir)
    result2 = run_pip('install', '-e', tmpdir)
    assert (join(env.site_packages, 'virtualenv.egg-link') in result2.files_created), result2.files_created.keys()
    result3 = run_pip('uninstall', '-y', 'virtualenv', expect_error=True)
    assert diff_states(result.files_before, result3.files_after, ignore=['env/build', 'cache']).values() == [{}, {}, {}]

def test_uninstall_from_reqs_file():
    """
    Test uninstall from a requirements file.
    
    """
    reset_env()
    write_file('test-req.txt', textwrap.dedent("""\
        -e svn+http://svn.colorstudy.com/INITools/trunk#egg=initools-dev
        # and something else to test out:
        PyLogo<0.4
        """))
    result = run_pip('install', '-r', 'test-req.txt')
    result2 = run_pip('uninstall', '-r', 'test-req.txt', '-y')
    assert diff_states(result.files_before, result2.files_after, ignore=['env/build', 'cache', 'src/initools']).values() == [{}, {}, {}]

