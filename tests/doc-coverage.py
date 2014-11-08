#!/usr/bin/env python2
# -*- coding:utf-8 -*-

from os import path, pathsep, remove
from subprocess import call
from sys import exit


# Source: http://stackoverflow.com/a/377028/939364
def which(program):

    import os

    def is_exe(fpath):
        return path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for executable_path in os.environ["PATH"].split(pathsep):
            executable_path = executable_path.strip('"')
            exe_file = path.join(executable_path, program)
            if is_exe(exe_file):
                return exe_file

    return None


cwd = path.abspath(path.dirname(__file__))

sphinx_build = which("sphinx-build")
if not sphinx_build:
    sphinx_build = which("sphinx-build2")
call(u"\"{}\" -b coverage ../doc .".format(sphinx_build), shell=True, cwd=cwd)

exit_value = 0
for file_name in [u"c.txt", u"python.txt"]:
    file_path = path.join(cwd, file_name)
    with open(file_path) as fp:
        for index, line in enumerate(fp):
            pass
    lines_count = index + 1
    if lines_count > 3:
        print(u"Found undocumented public members.")
        exit_value = 1
        break

for file_name in [u"c.txt", u"python.txt", u"undoc.pickle"]:
    file_path = path.join(cwd, file_name)
    remove(file_path)

exit(exit_value)
