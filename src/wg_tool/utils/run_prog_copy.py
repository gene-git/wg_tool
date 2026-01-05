# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: © 2023-present Gene C <arch@sapience.com>
"""
External program execution
"""
# pylint: disable=too-many-arguments, too-many-positional-arguments
# pylint: disable=consider-using-with
from typing import (IO)
import os
import fcntl
import io
from select import select
import subprocess
from subprocess import SubprocessError


class _ProcWaitInfo:
    """
    Little Data class used while waiting process to complete
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, proc: subprocess.Popen, bstring: bytes | None):
        self.proc: subprocess.Popen = proc
        self.bstring: bytes | None = bstring

        self.has_stdout: bool = True
        self.has_stderr: bool = True
        self.has_stdin: bool = bool(bstring)
        self.data_pending: bool = True

        self.readlist: list[int | IO] = []
        self.writelist: list[int | IO] = []
        self.exceplist: list[int | IO] = []

        # init non-blocking
        self.nonblock()
        self.is_data_pending()

    def is_data_pending(self):
        """
        Any more data
        """
        self.data_pending = bool(self.has_stdout
                                 or self.has_stderr
                                 or self.has_stdin)

    def nonblock(self):
        """
        Mark IO channels non-blocking
        """
        proc = self.proc
        try:
            if proc.stdin:
                fcntl.fcntl(proc.stdin, fcntl.F_SETFL, os.O_NONBLOCK)

            if proc.stdout:
                fcntl.fcntl(proc.stdout, fcntl.F_SETFL, os.O_NONBLOCK)

            if proc.stderr:
                fcntl.fcntl(proc.stderr, fcntl.F_SETFL, os.O_NONBLOCK)

        except OSError as err:
            # Should not happen. Cross fingers and keep going.
            print(f'Error setting NONBLOCK: {err}')

    def update_select_iolists(self):
        """
        Update read/write lists for select
        """
        #
        # Subprocess Read list
        #
        self.readlist = []
        if self.has_stdout and self.proc.stdout:
            self.readlist.append(self.proc.stdout)

        if self.has_stderr and self.proc.stderr:
            self.readlist.append(self.proc.stderr)

        #
        # Subprocess Write list
        #
        self.writelist = []
        if self.has_stdin and self.proc.stdin:
            self.writelist = [self.proc.stdin]

        if not (self.readlist or self.writelist or self.exceplist):
            self.data_pending = False

        # No subprocess exception list


def run_prog(pargs: list[str],
             input_str: str | None = None,
             stdout: int = subprocess.PIPE,
             stderr: int = subprocess.PIPE,
             env: dict[str, str] | None = None,
             test: bool = False,
             verb: bool = False,
             ) -> tuple[int, str, str]:
    """
    Run external program using subprocess.

    Take care to handle large outputs (default buffer size
    is 8k). This avoids possible hangs should IO buffer fill up.

    non-blocking IO together with select() loop provides
    a robust methodology.

    Args:
        pargs (list[str]):
            The command + arguments to be run in standard list format.
            e.g. ['/usr/bin/sleep', '22'].

        input_str (str | None):
            Optional input to be fed to subprocess stdin.  Defaults to None.

        stdout (int):
            Subprocess stdout. Defaults to subprocess.PIPE

        stderr (int):
            Subprocess stderr. Defaults to subprocess.PIPE

        env (None | dict[str, str]):
            Optional to specify environment for subprocess to use.
            If not set, inherits from calling process as usual.

        test (bool):
            Flag - if true dont actually run anything.

        verb (bool):
            Flag - only used with test == True - prints pargs.

    Returns:
        tuple[retc: int, stdout: str, stderr: str]:
            retc is 0 when all is well.
            stdout is what the subprocess returns on it's stdout
            and stderr is what it's stderr return.

    Note that any input string is written in it's entirety in one
    shot to the subprocess. This should not be a problem.
    """
    if not pargs:
        return (0, '', '')

    if test:
        if verb:
            print(' '.join(pargs))
        return (0, '', '')

    #
    # Tee up any input - even if no "input string"
    # If no input string and process expects input
    # it would hang without input - so we always allow it.
    # Select() will tell us whether process needs it.
    #
    bstring: bytes | None = None
    stdin: int | None = None
    if input_str:
        bstring = input_str.encode('utf-8')
        stdin = subprocess.PIPE

    retc: int = -1
    output: str = ''
    errors: str = ''

    #
    # Start up the process
    #
    (okay, proc, errors) = _popen_proc(pargs, stdin, stdout, stderr, env)

    if not okay:
        return (1, '', errors)

    #
    # Wait for it to complete
    #
    (retc, output, errors) = _wait_for_proc(bstring, proc)

    return (retc, output, errors)


def _popen_proc(pargs: list[str],
                stdin: int | None,
                stdout: int = subprocess.PIPE,
                stderr: int = subprocess.PIPE,
                env: dict[str, str] | None = None,
                ) -> tuple[bool, subprocess.Popen | None, str]:
    """
    Popen the process to run

    Handle large output buffers using non-blocking IO
    together with select() and reading of buffers/pipes to ensure
    they never fill up and block.
    Without this, larger output can hang when IO buffer is full.

    Args:
        See run_prog()

    Returns:
        tuple[success: bool, proc: subprocess.Popen , error: str]
    """
    #
    # Popen the process
    #
    proc: subprocess.Popen | None = None
    try:
        proc = subprocess.Popen(pargs,
                                stdin=stdin,
                                stdout=stdout,
                                stderr=stderr,
                                env=env)

    except (OSError, FileNotFoundError, ValueError, SubprocessError) as err:
        return (False, proc, str(err))

    return (True, proc, '')


def _wait_for_proc(bstring: bytes | None,
                   proc: subprocess.Popen | None) -> tuple[int, str, str]:
    """
    Process has been opened, wait for process to complete.
    Read/Write any data as may be needed.

    Args:
        proc (subprocess.Popen):

    Returns:
        tuple[returncode: int, stdout: str, stderr: str]
    """
    output = ''
    errors = ''
    timeout = 30

    if not proc:
        return (-1, '', 'process not started by popen - giving up')

    pwi = _ProcWaitInfo(proc, bstring)
    returncode = proc.returncode
    all_done: bool = False

    while not all_done and (returncode is None or pwi.data_pending):
        returncode = proc.poll()
        pwi.update_select_iolists()

        if returncode:
            #
            # Process exited.
            # Allow final data check for possible unread buffered data.
            #
            all_done = True
            break

        if not pwi.data_pending:
            continue

        #
        # Handle data
        # Note if all_done ignore fail as just checking.
        #
        (okay, this_output, this_errors) = _check_for_data(pwi, timeout)
        output += this_output
        errors += this_errors
        pwi.is_data_pending()

        if not all_done and not okay:
            return (-1, output, errors)

    # all done.
    retc = proc.returncode
    if retc is None:
        # should never happen
        retc = -1

    return (retc, output, errors)


def _check_for_data(pwi: _ProcWaitInfo, timeout: int) -> tuple[bool, str, str]:
    """
    Check if have any data.

    Args:
        pwi (_ProcWaitInfo):
            The info needed to wait on any data

        timeout (int):
            timeout seconds for select()

    Returns:
        tuple[success: bool, stdout: str, stderr: str]
    """
    bufsiz = io.DEFAULT_BUFFER_SIZE

    proc: subprocess.Popen = pwi.proc
    bstring: bytes | None = pwi.bstring

    output: str = ''
    errors: str = ''

    try:
        pwi.update_select_iolists()
        ready = select(pwi.readlist, pwi.writelist, pwi.exceplist, timeout)
        read_ready = ready[0]
        write_ready = ready[1]

        try:
            if pwi.has_stdin and proc.stdin and proc.stdin in write_ready:
                proc.stdin.write(bstring)
                proc.stdin.flush()
                proc.stdin.close()
                pwi.has_stdin = False

            if pwi.has_stdout and proc.stdout and proc.stdout in read_ready:
                data = proc.stdout.read(bufsiz)
                if len(data) == 0:
                    pwi.has_stdout = False
                    proc.stdout.close()
                else:
                    output += str(data, 'utf-8', errors='ignore')

            if pwi.has_stderr and proc.stderr and proc.stderr in read_ready:
                data = proc.stderr.read(bufsiz)
                if len(data) == 0:
                    pwi.has_stderr = False
                    proc.stderr.close()
                else:
                    errors += str(data, 'utf-8', errors='ignore')

            pwi.is_data_pending()

        except (OSError, IOError, EOFError, ValueError) as err:
            # read/write
            return (False, output, str(err) + ':\n' + errors)

    except (OSError, ValueError) as err:
        # select
        return (False, output, str(err) + ':\n' + errors)

    return (True, output, errors)
