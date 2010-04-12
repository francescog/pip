
from os.path import abspath, join, dirname, pardir
from test_pip import here, reset_env, run_pip, pyversion

def test_correct_pip_version():
    """
    Check we are running proper version of pip in run_pip.
    
    """
    reset_env()

    # where this source distribution lives
    base = abspath(join(dirname(__file__), pardir))

    # output will contain the directory of the invoked pip
    result = run_pip('--version')

    # compare the directory tree of the invoked pip with that of this source distribution
    import re,filecmp
    dir = re.match(r'\s*pip\s\S+\sfrom\s+(.*)\s\([^(]+\)$', result.stdout.replace('\r\n','\n')).group(1)
    diffs = filecmp.dircmp(join(base,'pip'), join(dir,'pip'))

    # If any non-matching .py files exist, we have a problem: run_pip
    # is picking up some other version!  N.B. if this project acquires
    # primary resources other than .py files, this code will need
    # maintenance
    mismatch_py = [x for x in diffs.left_only + diffs.right_only + diffs.diff_files if x.endswith('.py')]
    assert not mismatch_py, 'mismatched source files in %r and %r'% (join(base,'pip'), join(dir,'pip'))

def test_distutils_configuration_setting():
    """
    Test the distutils-configuration-setting command (which is distinct from other commands).
    
    """
    #print run_pip('-vv', '--distutils-cfg=easy_install:index_url:http://download.zope.org/ppix/', expect_error=True)
    #Script result: python ../../poacheggs.py -E .../poacheggs-tests/test-scratch -vv --distutils-cfg=easy_install:index_url:http://download.zope.org/ppix/
    #-- stdout: --------------------
    #Distutils config .../poacheggs-tests/test-scratch/lib/python.../distutils/distutils.cfg is writable
    #Replaced setting index_url
    #Updated .../poacheggs-tests/test-scratch/lib/python.../distutils/distutils.cfg
    #<BLANKLINE>
    #-- updated: -------------------
    #  lib/python2.4/distutils/distutils.cfg  (346 bytes)

def test_install_from_pypi():
    """
    Test installing a package from PyPI.
    
    """
    e = reset_env()
    result = run_pip('install', '-vvv', 'INITools==0.2', expect_error=True)
    new_files = sorted(result.files_created.keys())
    assert (e.site_packages / 'INITools-0.2-py%s.egg-info' % pyversion) in result.files_created, sorted(result.files_created.keys())
    assert (e.site_packages / 'initools') in result.files_created, sorted(result.files_created.keys())

def test_editable_install():
    """
    Test editable installation.
    
    """
    e = reset_env()
    e.run('cp', '-r', e.base_path, '/tmp/p1')
    result = run_pip('install', '-e', 'INITools==0.2', expect_error=True)
    e.run('cp', '-r', e.base_path, '/tmp/p2')
    assert "--editable=INITools==0.2 should be formatted with svn+URL" in result.stdout
    assert len(result.files_created) == 1, result.files_created
    assert not result.files_updated, result.files_updated

def test_install_editable_from_svn():
    """
    Test checking out from svn.
    
    """
    e = reset_env()
    result = run_pip('install', '-e', 'svn+http://svn.colorstudy.com/INITools/trunk#egg=initools-dev', expect_error=True)
    egg_link = result.files_created[e.site_packages / 'INITools.egg-link']
    # FIXME: I don't understand why there's a trailing . here:
    assert egg_link.bytes.endswith('.'), egg_link.bytes
    assert egg_link.bytes[:-1].strip().endswith(e.env_path / 'src' / 'initools'), egg_link.bytes
    assert (e.site_packages / 'easy-install.pth') in result.files_updated
    assert e.relative_env_path/'src'/'initools' in result.files_created, result.files_created
    assert e.relative_env_path/'src'/'initools'/'.svn' in result.files_created, result.files_created

def test_install_dev_version_from_pypi():
    """
    Test using package==dev.
    
    """
    e = reset_env()
    result = run_pip('install', 'INITools==dev', expect_error=True)
    assert (e.site_packages / 'initools') in result.files_created, str(result.stdout)

def test_install_editable_from_git():
    """
    Test cloning from Git.
    
    """
    e = reset_env()
    result = run_pip('install', '-e', 'git://github.com/jezdez/django-feedutil.git#egg=django-feedutil', expect_error=True)
    egg_link = result.files_created[e.site_packages / 'django-feedutil.egg-link']
    # FIXME: I don't understand why there's a trailing . here:
    assert egg_link.bytes.endswith('.'), egg_link.bytes
    #remove trailing "\n." and check that django-feedutil was installed
    assert egg_link.bytes[:-1].strip().endswith(e.env_path/ 'src' / 'django-feedutil'), egg_link.bytes
    assert e.site_packages / 'easy-install.pth' in result.files_updated
    assert e.relative_env_path / 'src' / 'django-feedutil' in result.files_created
    assert e.relative_env_path / 'src' / 'django-feedutil/.git' in result.files_created

def test_install_editable_from_hg():
    """
    Test cloning from Mercurial.
    
    """
    e = reset_env()
    result = run_pip('install', '-e', 'hg+http://bitbucket.org/ubernostrum/django-registration/#egg=django-registration', expect_error=True)
    egg_link = result.files_created[e.site_packages / 'django-registration.egg-link']
    # FIXME: I don't understand why there's a trailing . here:
    assert egg_link.bytes.endswith('.'), egg_link.bytes
    #remove trailing "\n." and check that django-registration was installed
    assert egg_link.bytes[:-1].strip().endswith(e.env_path/ 'src' / 'django-registration'), egg_link.bytes
    assert e.site_packages / 'easy-install.pth' in result.files_updated
    assert e.relative_env_path / 'src' / 'django-registration' in result.files_created
    assert e.relative_env_path / 'src' / 'django-registration/.hg' in result.files_created


def test_vcs_url_final_slash_normalization():
    """
    Test that presence or absence of final slash in VCS URL is normalized.
    
    """
    reset_env()
    result = run_pip('install', '-e', 'hg+http://bitbucket.org/ubernostrum/django-registration#egg=django-registration', expect_error=True)
    assert 'pip-log.txt' not in result.files_created, result.files_created['pip-log.txt'].bytes

def test_install_editable_from_bazaar():
    """
    Test checking out from Bazaar.
    
    """
    e = reset_env()
    result = run_pip('install', '-e', 'bzr+http://bazaar.launchpad.net/%7Edjango-wikiapp/django-wikiapp/release-0.1/@174#egg=django-wikiapp', expect_error=True)
    egg_link = result.files_created[e.site_packages / 'django-wikiapp.egg-link']
    # FIXME: I don't understand why there's a trailing . here:
    assert egg_link.bytes.endswith('/test-scratch/src/django-wikiapp\n.'), egg_link.bytes
    assert (e.site_packages / 'easy-install.pth') in result.files_updated
    assert 'src/django-wikiapp' in result.files_created
    assert 'src/django-wikiapp/.bzr' in result.files_created

def test_vcs_url_urlquote_normalization():
    """
    Test that urlquoted characters are normalized for repo URL comparison.
    
    """
    reset_env()
    result = run_pip('install', '-e', 'bzr+http://bazaar.launchpad.net/~django-wikiapp/django-wikiapp/release-0.1#egg=django-wikiapp', expect_error=True)
    assert 'pip-log.txt' not in result.files_created, result.files_created['pip-log.txt'].bytes

