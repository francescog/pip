
from os.path import abspath, join, dirname, pardir
from test_pip import here, reset_env, get_env, run_pip, pyversion, lib_py

def test_working_cmake():
    """
    Test the presence of cmake
    """
    reset_env()
    env = get_env()
    result = env.run('cmake', '--version')
    assert "cmake version" in result.stdout, result.stdout

def test_install_ryppl_from_git():
    """
    Test cloning a ryppl package from Git.
    
    """
    reset_env()
    result = run_pip('ryppl_install', 'git://github.com/francescog/sample_ryppl_package.git', expect_error=True)
    print result
    print result.stdout
    print result.stderr
    assert None, "Command Implementation still missing"
    #egg_link = result.files_created[lib_py + 'site-packages/django-feedutil.egg-link']
    # FIXME: I don't understand why there's a trailing . here:
    #assert egg_link.bytes.endswith('/test-scratch/src/django-feedutil\n.'), egg_link.bytes
    #assert (lib_py + 'site-packages/easy-install.pth') in result.files_updated
    #assert 'src/django-feedutil' in result.files_created
    #assert 'src/django-feedutil/.git' in result.files_created


