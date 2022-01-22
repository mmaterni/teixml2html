#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pdb import set_trace


class Inp:
    """livello debug
    0: disattivato 
    1: attivato solo per msg=!...
    2: attivato sempre 

    input
    .  : exit
    -  : continua 
    ,  : non fa nulla ( non aggiorna last) ritorna ,
    ,x : non fa nulla ritorna x
    Args:
        debug_liv (int, optional): 0/1/2
    """

    def __init__(self):
        self.liv = 0
        self.last = '$'
        self.v = ''

    def set_liv(self, liv='0'):
        if self.liv < 0:
            return
        self.liv = int(liv)
        self.ok_prn = (self.liv > 0)

    def inp(self, p='', msg=''):
        if self.liv == 0:
            return ""
        ok = False
        if self.liv == 1 and msg.find('!') >= 0:
            ok = True
        elif self.liv == 2:
            ok = True
        if not ok:
            return ""

        if self.last == '$':
            self.last = p

        t0 = self.liv == 2 and self.v == ''
        t1 = self.last == p
        t2 = p.find(',') == 0
        t3 = p == '!'
        if t0 or t1 or t2 or t3:
            self.v = input(p+msg+'>')
            if self.v == '.':
                sys.exit()
            elif self.v == '-':
                self.liv = -1
            elif self.v != '':
                self.last = self.v
        return ""

    def help(self,msg):
        x = input(msg)
        if x == '.':
            sys.exit()
        elif x == '-':
            self.liv = 0
        return x
