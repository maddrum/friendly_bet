"""
Needed for when coverage.py is run.
More on that: https://coverage.readthedocs.io/en/stable/subprocess.html

The file will be copied automatically when you specify < SETUP_COVERAGE_PY > to be "on"
"""

import coverage

coverage.process_startup()
