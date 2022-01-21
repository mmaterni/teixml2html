#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import os

#os.chmod(path, 0o666)

# x|xml_tag|tag|keys|attrs|text|params|parent


def read_csv(csv_path):
    with open(csv_path, "r") as f:
        txt = f.read()
    txt = txt.replace(f"\{os.linesep}", "")
    csv = txt.split(os.linesep)
    lst_dip = []
    lst_int = []
    for row in csv:
        if row.strip() == '':
            continue
        if not row[0] in "xdi":
            continue
        fs = row.split('|')
        tp = fs[0]
        tag = fs[1]
        if tag == 'xml_tag':
            continue
        if tp == 'x':
            lst_dip.append(tag)
            lst_int.append(tag)
        elif tp == 'i':
            lst_int.append(tag)
        elif tp == 'd':
            lst_dip.append(tag)
    return sorted(lst_dip), sorted(lst_int)


def read_xml_list():
    s = open("xml_list.txt").read()
    lst = s.split(os.linesep)
    return lst


def find_xml_attr(xml_lst, tag, attr):
    xml = ''
    j = -1
    for i, x in enumerate(xml_lst):
        if x.find(f"<{tag}") > -1:
            if x.find(attr[0]) > -1:
                if len(attr) > 1:
                    if x.find(attr[1]) > -1:
                        xml = x
                        j = i
                else:
                    xml = x
                    j = i
        if xml != '':
            break
    return j, xml


def find_xml_tag(xml_lst, tag):
    xml = ''
    j = -1
    for i, x in enumerate(xml_lst):
        if x.find(f"<{tag}") > -1:
            xml = x
            j = i
            break
    return j, xml


def select_xml(xml_lst, tag_lst, d_i):
    ids = []
    for tag in tag_lst:
        p = tag.find('+')
        if p > -1:
            continue
        i,xml = find_xml_tag(xml_lst, tag)
        if xml != '':
            ids.append(i)
            pth = F"xml_test/{d_i}/{tag}.xml"
            open(pth, "w").write(xml)

    for tag in tag_lst:
        p = tag.find('+')
        if p < 0:
            continue
        sp = tag.split('+')
        t = sp[0]
        a = sp[1:]
        if len(a) > 2:
            input(tag)
        i,xml = find_xml_attr(xml_lst, t, a)
        if xml != '':
            tag = tag.replace('+', '_')
            pth = F"xml_test/{d_i}/{tag}.xml"
            open(pth, "w").write(xml)


def write_test():
    ls = read_xml_list()
    xml_lst = []
    for x in ls:
        xml = open(x, "r").read()
        xml_lst.append(xml)
    tag_path = "teimcfg/html.csv"
    lst_dip, lst_int = read_csv(tag_path)
    select_xml(xml_lst, lst_dip, "dip")
    select_xml(xml_lst, lst_int, "int")


if __name__ == "__main__":
    # le=len(sys.argv)
    write_test()
