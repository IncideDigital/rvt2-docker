#!/usr/bin/env python3
# This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# WARNING: This server is not intended to be used in a unsecured environment.
# It runs the RVT2, and it is supposed to be run as root. As a result,
# no authentication, authorization or parameter checking is done in this source:
# WARNING: ALL KIND OF INJECTIONS ARE POSSIBLE!!!!!

""" A simple server to control the rvt2 from a web page """

import os
from flask import Flask, request, abort, send_from_directory, safe_join
from flask_cors import CORS
import sys
import json
import subprocess
import configparser

app = Flask(__name__)
CORS(app)
config = configparser.ConfigParser()


def run_rvt2(jobname, casename='casename', source='source', path=None, params={}, background=True):
    """ Runs a command in a local rvt2.

    Params:
        jobname: the name of the job.
        casename: the name of the case.
        source: the name of the source.
        path: the optional path. If None, use the default value defined by the job.
        background: if False, returns the output from the rvt2. If True, returns the PID without waiting for the rvt2 to finish.

    Configuration section:
        :**rvt2_exec**: the absolute path to the rvt2 executable. Default: `/opt/rvt2/rvt2`.
        :**rvt2_extraconfig**: an extra configuration file, if needed. Default: `rvt2-server.cfg`.
        :**morgue**: path to the morgue. Default: `/morgue`.
    """
    command = [
        config.get('rvt2-server', 'rvt2_exec'),
        '-c', config.get('rvt2-server', 'rvt2_extraconfig'),
        '--morgue', config.get('rvt2-server', 'rvt2_morgue'),
        '--casename', casename,
        '--source', source,
        '-j', jobname]
    # if not in the background, get the output in json
    if not background:
        command.append('-p')
    # if a path if defined, add the path
    if path is not None:
        command.append(path)
    # if params are defined, add params
    if params:
        for param in params.keys():
            command.append('--param')
            command.append('{}={}'.format(param, params[param]))
    # Run the command
    if background:
        # background process: run using Popen and ignore output
        return dict(pid=subprocess.Popen(command, stdout=subprocess.DEVNULL).pid)
    else:
        # not background process: run usind check_output and return the output
        try:
            return subprocess.check_output(command).decode()
        except Exception:
            abort(500)


@app.route('/status/<casename>')
def status(casename):
    """ Get the status of the jobs on a casename """
    data = run_rvt2('status.json', casename=casename, background=False)
    # if there is no data: the status cannot be read (casename does not exists, no jobs yet)
    if not data:
        abort(404)
    return data


@app.route('/help/<job>/<casename>/<source>')
def help(job, casename, source):
    """ Get help for a job.
    This method needs casename and source to return the specific configuration of a job for that casename and source. """
    data = run_rvt2('help.json', casename=casename, source=source, path=job, background=False)
    if not data:
        abort(404)
    return data

@app.route('/available_cases')
def available_cases():
    """ Show available cases in the rvt2 """
    return run_rvt2('show_cases', background=False, params=dict(outfile='/dev/null'))

@app.route('/available_images/<casename>')
def available_images(casename):
    """ Show available cases in the rvt2 """
    return run_rvt2('show_images', casename=casename, background=False, params=dict(outfile='/dev/null'))

@app.route('/available_jobs')
def available_jobs():
    """ Show available jobs in the rvt2 """
    return run_rvt2('base.help.AvailableJobs', background=False)

@app.route('/new_job', methods=['POST'])
def new_job():
    """ Creates a new job.
    The request is a POST message with a JSON body `{job, casename, source, path, params{name, vlue}}`
    """
    content = request.json
    job = content.get('job', None)
    casename = content.get('casename', None)
    source = content.get('source', None)
    if not job or not casename or not source:
        abort(403)
    params = content.get('params', {})
    path = content.get('path', None)
    if path == '':
        path = None
    pid = run_rvt2(job, casename=casename, source=source, path=path, params=params, background=True)
    return dict(pid=pid)

@app.route('/morgue/<casename>/<source>/', defaults={'path': ''})
@app.route('/morgue/<casename>/<source>/<path:path>', methods=['GET'])
def get_path(casename, source, path):
    """ Get information about a path: if it is a file, return the file. If it is a directory, return information about the directory
    """
    safepath = safe_join(config.get('rvt2-server', 'rvt2_morgue'), casename, source, path)
    print(safepath, path)
    if os.path.exists(safepath):
        if os.path.isdir(safepath):
            return list_directory(casename, source, path)
        else:
            sourcepath = safe_join(config.get('rvt2-server', 'rvt2_morgue'), casename, source)
            return send_from_directory(sourcepath, path)
    else:
        abort(404)

def list_directory(casename, source, dirname=None):
    if dirname:
        absdirname = safe_join(config.get('rvt2-server', 'rvt2_morgue'), casename, source, dirname)
        parent = os.path.dirname(dirname)
    else:
        absdirname = safe_join(config.get('rvt2-server', 'rvt2_morgue'), casename, source)
        parent = None
    if not os.path.exists(absdirname):
        abort(404)
    if not os.path.isdir(absdirname):
        abort(400)
    items = []
    for path in os.listdir(absdirname):
        itempath = os.path.join(absdirname, path)
        itemdata = dict(
            name=path,
            type=('directory' if os.path.isdir(itempath) else 'file')
        )
        itemdata.update(item_stats(itempath))
        items.append(itemdata)
    return dict(dirname=dirname, parent=parent, items=items)

def item_stats(itempath):
    stats = os.stat(itempath)
    return dict(
        mode=stats.st_mode,
        st_ino=stats.st_ino,
        st_dev=stats.st_dev,
        uid=stats.st_uid,
        gid=stats.st_gid,
        size=stats.st_size,
        atime=stats.st_atime,
        mtime=stats.st_mtime,
        ctime=stats.st_ctime
    )

if __name__ == '__main__':
    # If there is a configuration file in the command line, load it
    if len(sys.argv) == 2:
        config.read(sys.argv[1])
    else:
        # else, load default configuration
        config.read(os.path.join(os.path.dirname(__file__)), 'rvt2-server.cfg')
    # run the server using simple flask
    app.run(
        config.get('rvt2-server', 'host'),
        port=config.getint('rvt2-server', 'port'),
        debug=config.getboolean('rvt2-server', 'debug'))
