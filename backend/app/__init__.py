"""Backend application package.

This package is restricted to Python 3.11.x.
"""

import sys


if sys.version_info[:2] != (3, 11):
	current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
	raise RuntimeError(
		"Text-to-SQL backend requires Python 3.11.x. "
		f"Current version: {current_version}."
	)

