"""
pytest runner for the scripts.
"""
import os
import subprocess
import pytest

# conftest.py
import pytest

@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.node.fspath.dirname)

@pytest.mark.parametrize("script", [
        "./clean.sh",
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

