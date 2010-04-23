
from os.path import abspath, join, dirname, pardir
from test_pip import here, reset_env, run_pip, pyversion, lib_py

def test_install_editable_from_git():
    """
    Test cloning a ryppl package from Git.
    
    """
    reset_env()
    result = run_pip('ryppl_install', '-e', 'git://github.com/francescog/sample_ryppl_package.git', expect_error=True)
    #egg_link = result.files_created[lib_py + 'site-packages/django-feedutil.egg-link']
    # FIXME: I don't understand why there's a trailing . here:
    #assert egg_link.bytes.endswith('/test-scratch/src/django-feedutil\n.'), egg_link.bytes
    #assert (lib_py + 'site-packages/easy-install.pth') in result.files_updated
    #assert 'src/django-feedutil' in result.files_created
    #assert 'src/django-feedutil/.git' in result.files_created


