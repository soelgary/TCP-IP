#!/usr/bin/python2
import sys
import filecmp

def compare(argv):
	print filecmp.cmp(argv[1], argv[2])

if __name__ == "__main__":
  compare(sys.argv)