#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib as pl
from teixml2html import Xml2Html
import sys


def files_of_dir(d, e):
    p = pl.Path(d)
    fs = sorted(list(p.glob(e)))
    return fs


def exec_test(d_i):
    dip_int = "dip" if d_i == 'd' else "int"
    d = f"xml_test/{dip_int}/"
    lst = files_of_dir(d, "*")
    #x2h = Xml2Html()
    try:
        for x in lst:
            xml_path = f'{x}'
            html_path = xml_path.replace("xml", "html")
            wtn = "par1"
            # print(xml_path)
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
