#!/usr/bin/env python
import os, sys

pyversion = sys.version[:3]
lib_py = 'lib/python%s/' % pyversion
here = os.path.dirname(os.path.abspath(__file__))
base_path = os.path.join(here, 'test-scratch')
download_cache = os.path.join(here, 'test-cache')
if not os.path.exists(download_cache):
    os.makedirs(download_cache)

# Tweak the path so we can find scripttest
sys.path = [os.path.join(os.path.dirname(here), 'scripttest')] + sys.path
from scripttest import TestFileEnvironment

if 'PYTHONPATH' in os.environ:
    del os.environ['PYTHONPATH']

try:
    any
except NameError:
    def any(seq):
        for item in seq:
            if item:
                return True
        return False

def clear_environ(environ):
    return dict(((k, v) for k, v in environ.iteritems()
                if not k.lower().startswith('pip_')))

def virtualenv_bin_dir(path):
    if sys.platform == 'win32':
        return os.path.join(path, 'Scripts')
    else:
        return os.path.join(path, 'bin')

def install_setuptools(env):
    easy_install = os.path.join(env.bin_dir, 'easy_install')
    version = 'setuptools==0.6c11'
    if sys.platform != 'win32':
        return env.run(easy_install, version)
    
    import tempfile, shutil
    tempdir = tempfile.mkdtemp()
    try:
        shutil.copy2(easy_install+'.exe', tempdir)
        shutil.copy2(easy_install+'-script.py', tempdir)
        return env.run(os.path.join(tempdir, 'easy_install'), version)
    finally:
        shutil.rmtree(tempdir)
            
    
env = None
def reset_env(environ=None):
    global env
    if not environ:
        environ = os.environ.copy()
        environ = clear_environ(environ)
        environ['PIP_DOWNLOAD_CACHE'] = download_cache
    environ['PIP_NO_INPUT'] = '1'
    environ['PIP_LOG_FILE'] = './pip-log.txt'

    env = TestFileEnvironment(base_path, ignore_hidden=False, environ=environ, split_cmd=False)
    env.run(sys.executable, '-m', 'virtualenv', '--no-site-packages', env.base_path)

    # put the test-scratch virtualenv's bin dir first on the script path
    env.script_path.insert(0, virtualenv_bin_dir(env.base_path))

    # Figure out where the virtualenv is putting things
    where = env.run(sys.executable, '-c', 
                    'import virtualenv;'
                    'virtualenv.logger = virtualenv.Logger([]);'
                    'print repr(virtualenv.path_locations(%r))'%env.base_path)
    env.home_dir, env.lib_dir, env.inc_dir, env.bin_dir = eval(where.stdout.strip())

    # make sure we have current setuptools to avoid svn incompatibilities
    install_setuptools(env)

    # Uninstall whatever version of pip came with the virtualenv
    env.run(os.path.join(env.bin_dir,'pip'), 'uninstall', '-y', 'pip')

    # Install this version instead
    env.run('python', 'setup.py', 'install', cwd=os.path.dirname(here))
    print env.run('pip', '--version')

def run_pip(*args, **kw):
    args = ('pip',) + args
    #print >> sys.__stdout__, 'running', ' '.join(args)
    result = env.run(*args, **kw)
    return result

def write_file(filename, text):
    f = open(os.path.join(base_path, filename), 'w')
    f.write(text)
    f.close()

def get_env():
    return env

# FIXME ScriptTest does something similar, but only within a single
# ProcResult; this generalizes it so states can be compared across
# multiple commands.  Maybe should be rolled into ScriptTest?
def diff_states(start, end, ignore=None):
    """
    Differences two "filesystem states" as represented by dictionaries
    of FoundFile and FoundDir objects.

    Returns a dictionary with following keys:

    ``deleted``
        Dictionary of files/directories found only in the start state.

    ``created``
        Dictionary of files/directories found only in the end state.

    ``updated``
        Dictionary of files whose size has changed (FIXME not entirely
        reliable, but comparing contents is not possible because
        FoundFile.bytes is lazy, and comparing mtime doesn't help if
        we want to know if a file has been returned to its earlier
        state).

    Ignores mtime and other file attributes; only presence/absence and
    size are considered.
    
    """
    ignore = ignore or []
    start_keys = set([k for k in start.keys()
                      if not any([k.startswith(i) for i in ignore])])
    end_keys = set([k for k in end.keys()
                    if not any([k.startswith(i) for i in ignore])])
    deleted = dict([(k, start[k]) for k in start_keys.difference(end_keys)])
    created = dict([(k, end[k]) for k in end_keys.difference(start_keys)])
    updated = {}
    for k in start_keys.intersection(end_keys):
        if (start[k].size != end[k].size):
            updated[k] = end[k]
    return dict(deleted=deleted, created=created, updated=updated)

if __name__ == '__main__':
    sys.stderr.write("Run pip's tests using nosetests. Requires virtualenv, ScriptTest, and nose.\n")
    sys.exit(1)
