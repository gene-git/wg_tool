"""
pytest runner for the scripts.
"""
import os
import subprocess
import pytest


@pytest.mark.parametrize("script", [
        "./create-example-1",
        "./create-example-2",
        "./create-example-3",
        "./create-example-4",
        "./check-results",
        ]
)
def test_execute_bash_scripts(script):
    #
    # Run each test script
    #
    
    result = subprocess.run(
        [script],
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, (
        f"Script Fail: {os.path.basename(script)}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

