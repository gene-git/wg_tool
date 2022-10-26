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

def run_prog_input(pargs, text, test=False, verb=False):
    """
    run external program using subprocess and send input to it's stdin
    """
    # pylint: disable=C0301,R1732
    if pargs and pargs != [] :
        if test:
            if verb:
                cout = ' '.join(pargs) + '\n'
                print(f'Run_prog_input : {cout}')
                return [0, None, None]
        proc = subprocess.Popen(pargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    text=True)
        if proc:
            [output, errors] = proc.communicate(input=text)
            return [0, output, errors]
    return [0, None, None]
