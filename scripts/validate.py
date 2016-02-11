#!/usr/bin/env python

import json
import sys

if __name__ == "__main__":
    with open("config.json", "r") as f:
        try:
            contents = f.read()
            json.loads(contents)
            print "config.json validated successfully."
        except ValueError as e:
            print "config.json failed validation: %s" % (e.message)
            sys.exit(2)

