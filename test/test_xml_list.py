#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import pathlib as pl
from teixml2html import Xml2Html
import sys


def files_of_dir(d, e):
    p = pl.Path(d)
    ls = p.glob(e)
    lst = list(ls)
    fs = sorted(lst)
    return fs


def exec_test(d_i):
    dip_int = "dipl" if d_i == 'd' else "inter"
    d = f"xml_test/{dip_int}/"
    print(d)
    lst = files_of_dir(d,"*.xml")
    try:
        for x in lst:
            xml_path = f'{x}'
            print(xml_path)
            html_path = xml_path.replace("xml", "html")
            wtn = "witness"
            Xml2Html().write_html(xml_path,
                                  html_path,
                                  "",
                                  wtn,
                                  d_i,
                                  "w",
                                  1)
    except Exception as e:
        sys.exit(e)


if __name__ == "__main__":
    exec_test("d")
    exec_test("i")
