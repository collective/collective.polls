"""Upgrade to 3000: from any 2.x profile version to 3.0.

No 2.x upgrade step ever changed stored data, so one step serves every 2.x
version. It is idempotent and never drops vote data.
"""
