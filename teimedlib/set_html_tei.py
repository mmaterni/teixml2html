#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pdb import set_trace
import sys
from io import StringIO
from lxml.html import etree
from lxml.cssselect import CSSSelector
from teimedlib.ualog import Log


class HtmlTeiAdjust(object):

    def __init__(self):
        self.root = None
        self.logerr = Log("w")
        self.logerr.open("log/set_html_tei.ERR.log", 1)

    def set_root(self, src):
        try:
            # parser = etree.HTMLParser()
            parser = etree.HTMLParser(
                strip_cdata=True,
                remove_blank_text=True,
                default_doctype=False,
            )
            self.root = etree.parse(StringIO(src), parser)
        except Exception as e:
            self.logerr.log("ERROR set_html_tei.set_root()")
            self.logerr.log(e)
            sys.exit(1)

    def select_all(self, expr, node=None):
        node = self.root if node is None else node
        try:
            nd_lst = CSSSelector(expr)(node)
            return nd_lst
        except Exception as e:
            self.logerr.log("ERROR set_html_tei.select_all()")
            self.logerr.log(e)
            sys.exit(1)

    # numerateLines: function (ref) {
    #     const eps_dip_int = document.querySelectorAll("div.div_text");
    #     for (const eps of eps_dip_int) {
    #         const lines = eps.querySelectorAll("span.lnum");
    #         for (let i = 0; i < lines.length; i++) {
    #             lines[i].innerHTML = `${i + 1}`;
    #             const w = lines[i].closest("div.w");
    #         }
    #     }
    # },
    def numerate_lines(self):
        try:
            eps_dip_int = self.select_all("div.div_text")
            for eps in eps_dip_int:
                lines = self.select_all("span.lnum", eps)
                for i, line in enumerate(lines):
                    line.text = f'{i+1}'
        except Exception as e:
            self.logerr.log("ERROR set_html_tei.numerate_lines()")
            self.logerr.log(e)
            sys.exit(1)

    # wordbroken: function (ref) {
    #     const eps_dip_int = document.querySelectorAll("div.div_text");
    #     for (const eps of eps_dip_int) {
    #         const brokens = eps.querySelectorAll("span.broken");
    #         for (const brk of brokens) {
    #             if (!brk.closest("div.w"))
    #                 brk.remove();
    #         }
    #     }
    # }
    def wordbroken(self):
        try:
            eps_dip_int = self.select_all("div.div_text")
            for eps in eps_dip_int:
                brokens = self.select_all("span.broken", eps)
                for brk in brokens:
                    parent = brk.getparent()
                    cls = parent.attrib.get('class')
                    cls_lst = cls.split(" ")
                    if not "w" in cls_lst:
                        parent.remove(brk)
        except Exception as e:
            self.logerr.log("ERROR set_html_tei.wordbroken()")
            self.logerr.log(e)
            sys.exit(1)

    def get_html(self):
        try:
            #   method='html',
            html = etree.tostring(self.root,
                                  xml_declaration=None,
                                  encoding='unicode',
                                  with_tail=True,
                                  pretty_print=False,
                                  standalone=None,
                                  doctype=None,
                                  exclusive=False,
                                  inclusive_ns_prefixes=None,
                                  strip_text=False)
        except etree.ParseError as e:
            self.logerr.log("ERROR set_html_tei.get_html()")
            self.logerr.log(e)
            sys.exit(1)
        return html


def set_html_tei(html):
    slc = HtmlTeiAdjust()
    slc.set_root(html)
    slc.numerate_lines()
    slc.wordbroken()
    html_tei = slc.get_html()
    return html_tei
