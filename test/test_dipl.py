#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os
import pathlib as pl
from teixml2html import do_main


def exec_test(name):
    xml_path = f"xml_test/dip/{name}"
    html_path = xml_path.replace("xml", "html")
    wtn = "par1"
    do_main(xml_path, html_path, "", wtn,"d", "w")

if __name__ == "__main__":
    n=sys.argv[1]
    exec_test(n)
