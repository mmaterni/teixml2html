#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import argparse
import teimedlib.pathutils as ptu
from teixml2html import Xml2Html
import json
from pdb import set_trace

__date__ = "22-03-2022"
__version__ = "0.0.3"
__author__ = "Marta Materni"

"""
scrive un file <path_file>.json utilizzando anche valori di defuault
dei parametri.
lancia 
teixml2html.py
utilizzando il file json crato
il file può essere utilizzato per lanciare
teizml2html.py

"""


def set_conf_json(xml_path, tag_path, di, wtn, pid):
    html_cfg = {
        "html_params": {
            "_WTN_": wtn,
            "text_null": "",
            "_QA_": "\"",
            "_QC_": "\""
        },
        "html_tag_file": tag_path,
        "html_tag_type": di+":txt",
        "dipl_inter": di,
        "before_id": pid
    }
    try:
        dip_int = "dipl" if di == 'd' else "inter"
        conf_path = xml_path.replace(".xml", f"_{dip_int}.json")
        s = json.dumps(html_cfg, indent=2)
        # AAA fu.write_path_file(conf_path, s)
        ptu.make_dir_of_file(conf_path)
        with open(conf_path, "w") as f:
            f.write(s)

    except Exception as e:
        msg = f"ERROR {xml_path}  write_default_conf()\n{e}"
        sys.exit(msg)
    return conf_path


def do_main(xml,
            html,
            tag,
            di,
            wtn,
            pid,
            wa,
            deb):
    # set_trace()
    json_path = set_conf_json(xml, tag, di, wtn, pid)
    Xml2Html().write_html(xml, html, json_path, wa, deb)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    if len(sys.argv) == 1:
        print("release: %s  %s" % (__version__, __date__))
        parser.print_help()
        sys.exit(1)
    parser.add_argument('-i',
                        dest="xml",
                        required=True,
                        metavar="file-input",
                        help="-i <file_in.xml>")
    parser.add_argument('-o',
                        dest="html",
                        required=True,
                        metavar="file-output",
                        help="-o <file_out.html>")

    parser.add_argument('-t',
                        dest="tag",
                        required=False,
                        default="teimcfg/html.csv",
                        metavar="file tag.csv",
                        help="-t <tag_file.csv> (default:teimcfg/html.csv)")
    parser.add_argument('-di',
                        dest="di",
                        required=False,
                        default="d",
                        metavar="",
                        help="-di d/i  (d)iplomat/i)terpret default:d)")
    parser.add_argument('-p',
                        dest="pid",
                        required=False,
                        default="",
                        metavar="",
                        help="-p <X> (prefix id default:K )")
    parser.add_argument('-wt',
                        dest="wtn",
                        required=False,
                        metavar="",
                        default="witness",
                        help="-wt <witness> default:witness")
    parser.add_argument('-wa',
                        dest="wa",
                        required=False,
                        metavar="",
                        default="w",
                        help="-wa w/a (w)rite a)ppend html default:w)")
    parser.add_argument('-d',
                        dest="deb",
                        required=False,
                        metavar="",
                        default=0,
                        help="-d 0/1/2 (debug level default:0)")
    args = parser.parse_args()
    do_main(args.xml,
            args.html,
            args.tag,
            args.di,
            args.wtn,
            args.pid,
            args.wa,
            args.deb)
