#!/usr/bin/python3
import argparse
import os
import re
import subprocess
import yaml
from collections import OrderedDict
from flask import Flask, request
from fnmatch import fnmatchcase

if __name__ != '__main__':
    raise ImportError('not a importable module');

# accept cli options
parser = argparse.ArgumentParser()
parser.add_argument('--host', default='0.0.0.0')
parser.add_argument('-p', '--port', type=int, default=8001)
parser.add_argument('-d', '--debug', action='store_true')
cli_args = parser.parse_args()

# turn a dict into an OrderedDict, so that matches happen consistently in order
def yaml_construct_dict(loader, node):
    return OrderedDict(loader.construct_omap(node))
yaml.add_constructor(OrderedDict, yaml_construct_dict)

with open('config.yml', 'r') as f:
    config = yaml.load(f)

# flask application

app = Flask(__name__)

@app.route('/')
def index():
    'For debugging purposes'
    return 'the dash button server is running\n'

@app.route('/dash')
def dash():
    'The main handler'
    args = request.args # mode, mac, ip, host
    print('\n\n' + '-' * 80 + '\nprocessing %s (%s) %s event' %
          (args['mac'], args['host'], args['mode']))

    cmd = None
    try:
        cmd = get_cmd(args['mac'], args['host'], args['mode'])
    except:
        print('found no handler')

    if cmd is None:
        print('doing nothing')
    else:
        print('found handler')
        run_cmd(cmd, request.args)

    return 'okay\n'

def get_cmd(mac, host, mode):
    '''
    We allow the '+' operator to be used to join multiple keys with the same
    value.

    For example, we allow different actions on add/del/old events, and to
    simplify the syntax for certain combinations for event handlers that work
    across multiple modes, we rewrite::

      add+old: mplayer chime.mp3

    as::

      add: mplayer chime.mp3
      old: mplayer chime.mp3

    This goes further though, because this same syntax can be used with
    hostnames and syntax from the ``fnmatch`` module::

      # spaces are also allowed around the + operator
      laptop + DE:AD:BE:EF:*:
        add+old: mplayer hello.ogg
        del: mplayer goodbye.ogg

    which expands to::
    
      laptop:
        add: mplayer hello.ogg
        old: mplayer hello.ogg
        del: mplayer goodbye.ogg
      DE:AD:BE:EF:*:
        add: mplayer hello.ogg
        old: mplayer hello.ogg
        del: mplayer goodbye.ogg
    '''
    plus_re = re.compile(r'\s*\+\s*')
    def match(pattern, value):
        return any(fnmatchcase(value.lower(), p.lower())
                   for p in plus_re.split(pattern))

    for host_expr, handlers in config.items():
        if match(host_expr, mac) or match(host_expr, host):
            print(host_expr, mode, handlers)
            for mode_expr, cmd in handlers.items():
                print(mode_expr, cmd)
                if match(mode_expr, mode):
                    print('match b')
                    return cmd
            raise KeyError()
    raise KeyError()

def run_cmd(cmd, request_args):
    '''
    Executes the command in a subshell.

    ``$MAC``, ``$MODE``, ``$IP``, and ``$HOST`` environment variables are
    provided to help with more advanced scripts.
    '''
    print('running command: `%s`' % cmd)
    env = dict(os.environ)
    env.update({k.upper(): request_args[k]
                for k in ('mac', 'mode', 'ip', 'host')})
    subprocess.check_call(cmd, shell=True, env=env)

app.run(host=cli_args.host, port=cli_args.port, debug=cli_args.debug)
