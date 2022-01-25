#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from teixml2html import do_main


def exec_test(name):
    xml_path = f"xml_test/dipl/{name}"
    html_path = xml_path.replace("xml", "html")
    wtn = "WITNESS"
    do_main(xml_path, html_path, "", wtn, "d", "w")


if __name__ == "__main__":
    le = len(sys.argv)
    if le == 1:
        print("")
        print("file in xml_test/dipl")
        print("test_dipl.py file_name.xml")
        sys.exit()
    n = sys.argv[1]
    exec_test(n)
