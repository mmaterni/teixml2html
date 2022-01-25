#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pathlib as pl
import tx2h
import sys
from pdb import set_trace
from teimedlib import file_utils as fu


def files_of_dir(path_str, match=None):
    path = pl.Path(path_str)
    lst=[x for x in path.glob(match)]
    return lst

def exec_test(d_i):
    dip_int = "dipl" if d_i == 'd' else "inter"
    d = f"xml_test/{dip_int}/"
    print(d)
    lst = files_of_dir(d, "*.xml")
    try:
        for x in lst:
            xml_path = f'{x}'
            html_path = xml_path.replace("xml", "html")
            tx2h.do_main(xml_path,
                         html_path,
                         "teimcfg/html.csv",
                         d_i,
                         "witness",
                         "K",
                         "w",
                         1)
    except Exception as e:
        sys.exit(e)

if __name__ == "__main__":
    exec_test("d")
    exec_test("i")
