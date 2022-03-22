#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import sys
import argparse
import os
from teimedlib.ualog import Log
import teimedlib.pathutils as ptu

__date__ = "'22-03-2021"
__version__ = "0.1.1"
__author__ = "Marta Materni"

logerr = Log("a")

 
if __name__ == "__main__":
    logerr.open("log/writehtml.ERR.log", 1)
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit()
    try:
        parser.add_argument('-i',
                            dest="html",
                            required=False,
                            metavar="",
                            default="",
                            help="-i <html>")
        parser.add_argument('-o',
                            dest="ou",
                            required=True,
                            metavar="",
                            help="-o <file_out.html>")
        parser.add_argument('-wa',
                            dest="wa",
                            required=False,
                            metavar="",
                            default="a",
                            help="[-wa w/a (w)rite a)ppend) default a")
        args = parser.parse_args()
        html_ou = args.ou 
        ptu.make_dir_of_file(html_ou)
        html = args.html
        write_append = args.wa
        with open(html_ou, write_append) as f:
            f.write(html+os.linesep)
    except Exception as e:
        logerr.log("ERROR writehtml.py")
        logerr.log(e)
        sys.exit(1)
