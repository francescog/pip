
import tempfile
import textwrap
from test_pip import here, reset_env, run_pip, clear_environ, write_file
import os

def test_options_from_env_vars():
    """
    Test if ConfigOptionParser reads env vars (e.g. not using PyPI here)
    
    """
    environ = clear_environ(os.environ.copy())
    environ['PIP_NO_INDEX'] = '1'
    reset_env(environ)
    result = run_pip('install', '-vvv', 'INITools', expect_error=True)
    assert "Ignoring indexes:" in result.stdout, str(result)
    assert "DistributionNotFound: No distributions at all found for INITools" in result.stdout

def test_command_line_options_override_env_vars():
    """
    Test that command line options override environmental variables.
    
    """
    environ = clear_environ(os.environ.copy())
    environ['PIP_INDEX_URL'] = 'http://pypi.appspot.com/'
    reset_env(environ)
    result = run_pip('install', '-vvv', 'INITools', expect_error=True)
    assert "Getting page http://pypi.appspot.com/INITools" in result.stdout
    reset_env(environ)
    result = run_pip('install', '-vvv', '--index-url', 'http://download.zope.org/ppix', 'INITools', expect_error=True)
    assert "http://pypi.appspot.com/INITools" not in result.stdout
    assert "Getting page http://download.zope.org/ppix" in result.stdout

def test_command_line_append_flags():
    """
    Test command line flags that append to defaults set by environmental variables.
    
    """
    environ = clear_environ(os.environ.copy())
    environ['PIP_FIND_LINKS'] = 'http://pypi.pinaxproject.com'
    reset_env(environ)
    result = run_pip('install', '-vvv', 'INITools', expect_error=True)
    assert "Analyzing links from page http://pypi.pinaxproject.com" in result.stdout
    reset_env(environ)
    result = run_pip('install', '-vvv', '--find-links', 'http://example.com', 'INITools', expect_error=True)
    assert "Analyzing links from page http://pypi.pinaxproject.com" in result.stdout
    assert "Analyzing links from page http://example.com" in result.stdout

def test_config_file_override_stack():
    """
    Test config files (global, overriding a global config with a
    local, overriding all with a command line flag).
    
    """
    f, config_file = tempfile.mkstemp('-pip.cfg', 'test-')
    environ = clear_environ(os.environ.copy())
    environ['PIP_CONFIG_FILE'] = config_file # set this to make pip load it
    reset_env(environ)
    write_file(config_file, textwrap.dedent("""\
        [global]
        index-url = http://download.zope.org/ppix
        """))
    result = run_pip('install', '-vvv', 'INITools', expect_error=True)
    assert "Getting page http://download.zope.org/ppix/INITools" in result.stdout
    reset_env(environ)
    write_file(config_file, textwrap.dedent("""\
        [global]
        index-url = http://download.zope.org/ppix
        [install]
        index-url = http://pypi.appspot.com/
        """))
    result = run_pip('install', '-vvv', 'INITools', expect_error=True)
    assert "Getting page http://pypi.appspot.com/INITools" in result.stdout
    result = run_pip('install', '-vvv', '--index-url', 'http://pypi.python.org/simple', 'INITools', expect_error=True)
    assert "Getting page http://download.zope.org/ppix/INITools" not in result.stdout
    assert "Getting page http://pypi.appspot.com/INITools" not in result.stdout
    assert "Getting page http://pypi.python.org/simple/INITools" in result.stdout

def test_log_file_no_directory():
    """
    Test opening a log file with no directory name.
    
    """
    from pip.basecommand import open_logfile
    fp = open_logfile('testpip.log')
    fp.write('can write')
    fp.close()
    assert os.path.exists(fp.name)
    os.remove(fp.name)
