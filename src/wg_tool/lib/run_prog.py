# SPDX-License-Identifier: MIT
# Copyright (c) 2022,2023 Gene C
"""
wg-tool support utils`
"""
# pylint: disable=C0103
import subprocess

def run_prog(pargs,input_str=None,stdout=subprocess.PIPE,stderr=subprocess.PIPE):
    """
    run external program using subprocess
    """
    if not pargs:
        return [0, None, None]

    bstring = None
    if input_str:
        bstring = bytearray(input_str,'utf-8')

    ret = subprocess.run(pargs, input=bstring, stdout=stdout, stderr=stderr, check=False)
    retc = ret.returncode
    output = None
    errors = None
    if ret.stdout :
        output = str(ret.stdout, 'utf-8', errors='ignore')
    if ret.stderr :
        errors = str(ret.stderr, 'utf-8', errors='ignore')
    return [retc, output, errors]
