#!/usr/bin/env python
"""Schema Sync's command-line utility for administrative tasks."""

import os
import sys

from devcoffee_schema.config import settings


def main():
    """Run administrative tasks."""
    os.environ.setdefault("REGISTER_SETTINGS_MODULE", "devcoffee_schema.config")
    print(settings)


if __name__ == "__main__":
    main()
