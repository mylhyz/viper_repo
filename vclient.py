
from __future__ import print_function

import sys
import optparse
import os
import platform
import logging
import json

import subcommand
import subprocess2
import vclient_utils
import vclient_eval

__version__ = '0.0.1'


@subcommand.epilog("""示例:
  vclient sync
       checkout/update all local modules
""")
def CMDsync(parser, args):
    """checkout/update all local modules"""
    parser.add_option('-f', '--force', action='store_true',
                      help='force update even for unchanged modules')
    (options, args) = parser.parse_args(args)

    # 首先解析依赖文件
    deps_content = None
    deps_file = os.path.join(os.getcwd(), 'DEPS.py')
    if os.path.isfile(deps_file):
        deps_content = vclient_utils.FileRead(deps_file)
    local_scope = {}
    if deps_content:
        local_scope = vclient_eval.Parse(deps_content, deps_file)

    print(local_scope)

    deps = local_scope['deps']
    sync_url = local_scope['sync_url']

    cxx_modules_dir = os.path.join(os.getcwd(), 'cxx_modules')
    if not os.path.exists(cxx_modules_dir):
        os.mkdir(cxx_modules_dir)
    cache_dir = os.path.join(os.getcwd(), '.cache')
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)

    for dep in deps:
        strs = dep.split(':')
        name = strs[0]
        arch = strs[1]
        ver = strs[2]
        dep_url = sync_url+name+'_'+arch+"/"+ver+"/dist.zip"
        cache_file = os.path.join(cache_dir, name+'_'+arch+'_'+ver+'.zip')
        cache_file = vclient_utils.Download(
            dep_url, cache_file)
        target_cxx_modules_dir = os.path.join(cxx_modules_dir, name, arch)
        if not os.path.exists(target_cxx_modules_dir):
            os.makedirs(target_cxx_modules_dir)
        vclient_utils.Unzip(cache_file, target_cxx_modules_dir)

    return 0


CMDUpdate = CMDsync


class OptionParser(optparse.OptionParser):

    def __init__(self, **kwargs):
        optparse.OptionParser.__init__(
            self, version='%prog ' + __version__, **kwargs)

        # Some arm boards have issues with parallel sync.
        if platform.machine().startswith('arm'):
            jobs = 1
        else:
            jobs = max(8, vclient_utils.NumLocalCpus())

        self.add_option(
            '-j', '--jobs', default=jobs, type='int',
            help='Specify how many SCM commands can run in parallel; defaults to '
                 '%default on this machine')
        self.add_option(
            '-v', '--verbose', action='count', default=0,
            help='Produces additional output for diagnostics. Can be used up to '
                 'three times for more logging info.')

    def parse_args(self, args=None, _values=None):
        """Integrates standard options processing."""
        # Create an optparse.Values object that will store only the actual passed
        # options, without the defaults.
        actual_options = optparse.Values()
        _, args = optparse.OptionParser.parse_args(self, args, actual_options)
        # Create an optparse.Values object with the default options.
        options = optparse.Values(self.get_default_values().__dict__)
        # Update it with the options passed by the user.
        options._update_careful(actual_options.__dict__)

        levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
        logging.basicConfig(
            level=levels[min(options.verbose, len(levels) - 1)],
            format='%(module)s(%(lineno)d) %(funcName)s:%(message)s')
        if options.jobs < 1:
            self.error('--jobs must be 1 or higher')
        return (options, args)


def main(argv):
    """Doesn't parse the arguments here, just find the right subcommand to
    execute."""
    dispatcher = subcommand.CommandDispatcher(__name__)
    try:
        return dispatcher.execute(OptionParser(), argv)
    except KeyboardInterrupt:
        vclient_utils.GClientChildren.KillAllRemainingChildren()
        raise
    except (vclient_utils.Error, subprocess2.CalledProcessError) as e:
        print('Error: %s' % str(e), file=sys.stderr)
        return 1
    finally:
        vclient_utils.PrintWarnings()
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
