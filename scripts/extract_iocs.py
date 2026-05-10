#!/usr/bin/env python3
"""Extract IOCs from a text file using ioc-finder and print as JSON."""
import json
import sys

from ioc_finder import find_iocs

KNOWN_BENIGN = {"cisa.gov", "www.cisa.gov", "us-cert.cisa.gov", "attack.mitre.org"}

text = open(sys.argv[1]).read()
iocs = find_iocs(text)
iocs["domains"] = [d for d in iocs.get("domains", []) if d not in KNOWN_BENIGN]
print(json.dumps(iocs, default=list))
