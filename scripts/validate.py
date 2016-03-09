#!/usr/bin/env python

import yaml
import sys

if __name__ == "__main__":
    with open("config.yml", "r") as f:
        try:
            contents = f.read()
            yaml.load(contents)
            print "config.yml validated successfully."
        except ValueError as e:
            print "config.yml failed validation: %s" % (e.message)
            sys.exit(2)

