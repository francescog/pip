#!/usr/bin/env python
import os, sys, tempfile, shutil

pyversion = sys.version[:3]
lib_py = 'lib/python%s/' % pyversion
here = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(
    0, 
    os.path.join(os.path.dirname(__file__), os.path.pardir, 'scripttest'))

from scripttest import TestFileEnvironment

def install_requirement(req, where):
    """if the given package requirement isn't installed, install it in the specified directory
    """
    # Some of this logic stolen from ez_setup.py
    # At this point, we already have setuptools installed
    import pkg_resources, site

    try: pkg_resources.require(req)
    except pkg_resources.VersionConflict: pass
    except pkg_resources.DistributionNotFound: pass
    else: return

    try:
        from setuptools.command.easy_install import main as install
    except ImportError:
        from easy_install import main as install

    # we have to patch PYTHONPATH to include the installation
    # directory, to satisfy easy_install's nannying
    save_ppath = os.environ.get('PYTHONPATH', '')
    try:
        os.environ['PYTHONPATH'] = where
        install(['--install-dir', where, req])
        site.addsitedir(where)
    finally:
        os.environ['PYTHONPATH'] = save_ppath


def create_virtualenv(where):
    save_argv = sys.argv
    
    try:
        import virtualenv
        sys.argv = ['virtualenv', '--no-site-packages', where]
        virtualenv.main()
    finally: 
        sys.argv = save_argv

    return virtualenv.path_locations(where)

class TestPipEnvironment(TestFileEnvironment):

    def __init__(self):
        self.root_path = tempfile.mkdtemp()

        # We will set up a virtual environment at root_path.  
        scratch_path = os.path.join(self.root_path,'test-scratch')
        download_cache = os.path.join(self.root_path, 'test-cache')

        # where we'll create the virtualenv for testing
        env_path = os.path.join(self.root_path, 'test-env')

        # Where we'll put the setuptools and virtualenv packages (if necessary)
        aux_pkg_path = os.path.join(self.root_path, 'test-pkgs')
        sys.path.insert(0, aux_pkg_path)

        for d in (download_cache, aux_pkg_path, env_path):
            if not os.path.exists(d): 
                os.makedirs(d)

        # current environment, but wihtout all "PIP_" environment
        # variables...
        environ = dict( ((k, v) for k, v in os.environ.iteritems()
                         if not k.lower().startswith('pip_') 
                         # ...or PYTHONPATH
                         and not k.lower() == 'pythonpath') )

        # Prepare option defaults for pip.  Note that even though some
        # of their names don't appear elsewhere in our source, the
        # values of these variables *will* be used by
        # pip.baseparser.ConfigOptionParser.update_defaults(...)
        environ['PIP_DOWNLOAD_CACHE'] = download_cache
        environ['PIP_NO_INPUT'] = '1'
        environ['PIP_LOG_FILE'] = './pip-log.txt'

        # environ['DISTUTILS_DEBUG'] = 'YES'

        #
        # Make sure a recent-enough version of setuptools is on the path
        #
        required_setuptools_version = '0.6c11'
        try:
            # see if a recent-enough version of setuptools is already
            # installed.  We do this in a subprocess so that we don't
            # end up importing one that's too old, which would make it
            # impossible for ez_setup to install the newer one
            subprocess.check_call(
                ( sys.executable, '-c',
                  "import pkg_resources;pkg_resources.require('setuptools>=%s')"
                  % required_setuptools_version ))
        except:
            from ez_setup import use_setuptools
            use_setuptools(
                version=required_setuptools_version, download_delay=0, to_dir=aux_pkg_path)
        
        # make sure virtualenv is installed
        install_requirement('virtualenv', aux_pkg_path)
        
        # create the testing environment
        create_virtualenv(env_path)

        # Run everything else in that environment.  Setting PATH is
        # the only significant thing done by virtualenv's activate
        # script.
        #
        # TODO: this is a maintenance hazard.  How can we keep it in 
        # sync with bin/activate?
        bin = os.path.join(env_path,'bin')
        environ['PATH'] = os.path.pathsep.join((bin, environ['PATH']))

        super(TestPipEnvironment, self).__init__(
            scratch_path, ignore_hidden=False, environ=environ, split_cmd=False)

        # Now install ourselves there
        self.run('python', 'setup.py', 'install', cwd=os.path.join(here,os.pardir))
        
        # env.run(sys.executable, '-c', 'import os;os.mkdir("src")')

    def __del__(self):
        # shutil.rmtree(self.root_path)
        pass

try:
    any
except NameError:
    def any(seq):
        for item in seq:
            if item:
                return True
        return False

env = None
def reset_env():
    global env

    import tempfile
    env = TestPipEnvironment()

def run_pip(*args, **kw):
    # args = (sys.executable, '-c', 'import pip; pip.main()', '-E', env.base_path) + args
    # result = env.run(*args, **kw)
    # return result
    return get_env().run('pip', *args, **kw)

def write_file(filename, text):
    f = open(os.path.join(base_path, filename), 'w')
    f.write(text)
    f.close()

def get_env():
    if env is None:
        reset_env()
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
    sys.stderr.write("Run pip's tests using nosetests.\n")
    sys.exit(1)

