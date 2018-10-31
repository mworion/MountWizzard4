############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
# Python  v3.6.5
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest
import time
# external packages
from astropy import _erfa as erfaC
# local import
from mw4.base import erfa


class TestErfa(unittest.TestCase):

    def setUp(self):
        # necessary structs in classes
        self.ERFA = erfa.ERFA()

        # show performance
        self.show_perf = False
        # parameters for test

        self.ts = time.gmtime(0)

    def test_eraJd2cal(self):
        dj1 = 2458027.31896727 + 1.5
        dj2 = 0.0 - 0.81896727019

        start_time = time.clock()
        ok, iy, im, id, fd = self.ERFA.eraJd2cal(dj1, dj2)
        if self.show_perf:
            print(" ERFA Jd2cal     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        value = erfaC.jd2cal(dj1, dj2)
        if self.show_perf:
            print(" ERFA Jd2cal     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(ok, 0)
        self.assertEqual(value[0], iy)
        self.assertEqual(value[1], im)
        self.assertEqual(value[2], id)
        self.assertAlmostEqual(value[3], fd)

        dj2 = 0.0
        for j in range(2450000, 2460000):
            dj1 = j / 10

            ok, iy, im, id, fd = self.ERFA.eraJd2cal(dj1, dj2)
            value = erfaC.jd2cal(dj1, dj2)

            self.assertEqual(ok, 0)
            self.assertEqual(value[0], iy)
            self.assertEqual(value[1], im)
            self.assertEqual(value[2], id)
            self.assertAlmostEqual(value[3], fd)

        dj1 = 2400000.5
        dj2 = 50123.2
        ok, iy, im, id, fd = self.ERFA.eraJd2cal(dj1, dj2)
        value = erfaC.jd2cal(dj1, dj2)
        self.assertEqual(ok, 0)
        self.assertEqual(value[0], iy)
        self.assertEqual(value[1], im)
        self.assertEqual(value[2], id)
        self.assertAlmostEqual(value[3], fd)

        dj1 = 2451545.0
        dj2 = -1421.3
        ok, iy, im, id, fd = self.ERFA.eraJd2cal(dj1, dj2)
        value = erfaC.jd2cal(dj1, dj2)
        self.assertEqual(ok, 0)
        self.assertEqual(value[0], iy)
        self.assertEqual(value[1], im)
        self.assertEqual(value[2], id)
        self.assertAlmostEqual(value[3], fd)

        dj1 = 2450123.5
        dj2 = 0.2
        ok, iy, im, id, fd = self.ERFA.eraJd2cal(dj1, dj2)
        value = erfaC.jd2cal(dj1, dj2)
        self.assertEqual(ok, 0)
        self.assertEqual(value[0], iy)
        self.assertEqual(value[1], im)
        self.assertEqual(value[2], id)
        self.assertAlmostEqual(value[3], fd)

        dj1 = 2451967
        dj2 = 0
        ok, iy, im, id, fd = self.ERFA.eraJd2cal(dj1, dj2)
        value = erfaC.jd2cal(dj1, dj2)
        self.assertEqual(ok, 0)
        self.assertEqual(value[0], iy)
        self.assertEqual(value[1], im)
        self.assertEqual(value[2], id)
        self.assertAlmostEqual(value[3], fd)

    def test_eraCal2jd(self):
        start_time = time.clock()
        ok, djm0, djm = self.ERFA.eraCal2jd(self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday)
        if self.show_perf:
            print(" ERFA Cal2jd     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        value = erfaC.cal2jd(self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday)
        if self.show_perf:
            print(" ERFA Cal2jd     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(ok, 0)
        self.assertEqual(value[0], djm0)
        self.assertEqual(value[1], djm)

    def test_eraDtf2d(self):
        start_time = time.clock()
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        if self.show_perf:
            print(" ERFA Dtf2d      Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        value = erfaC.dtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        if self.show_perf:
            print(" ERFA Dtf2d      Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(0, ok)
        self.assertEqual(date1 + date2, value[0])

    def test_eraEpv00(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)

        start_time = time.clock()
        ok, pvh, pvb = self.ERFA.eraEpv00(date1, date2)
        if self.show_perf:
            print(" ERFA Epv00      Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        pvh_ref, pvb_ref = erfaC.epv00(date1, date2)
        if self.show_perf:
            print(" ERFA Epv00      Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(ok, 0)
        self.assertEqual(pvh[0][0], pvh_ref[0][0])
        self.assertEqual(pvh[0][1], pvh_ref[0][1])
        self.assertEqual(pvh[0][2], pvh_ref[0][2])
        self.assertEqual(pvh[1][0], pvh_ref[1][0])
        self.assertEqual(pvh[1][1], pvh_ref[1][1])
        self.assertEqual(pvh[1][2], pvh_ref[1][2])
        self.assertEqual(pvb[0][0], pvb_ref[0][0])
        self.assertEqual(pvb[0][1], pvb_ref[0][1])
        self.assertEqual(pvb[0][2], pvb_ref[0][2])
        self.assertEqual(pvb[1][0], pvb_ref[1][0])
        self.assertEqual(pvb[1][1], pvb_ref[1][1])
        self.assertEqual(pvb[1][2], pvb_ref[1][2])

    def test_eraObl06(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)

        start_time = time.clock()
        epsa = self.ERFA.eraObl06(date1, date2)
        if self.show_perf:
            print(" ERFA Obl06      Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        epsa_ref = erfaC.obl06(date1, date2)
        if self.show_perf:
            print(" ERFA Obl06      Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(epsa, epsa_ref)

    def test_eraPfw06(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)

        start_time = time.clock()
        gamb, phib, psib, epsa = self.ERFA.eraPfw06(date1, date2)
        if self.show_perf:
            print(" ERFA Pfw06      Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        gamb_ref, phib_ref, psib_ref, epsa_ref = erfaC.pfw06(date1, date2)
        if self.show_perf:
            print(" ERFA Pfw06      Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(gamb, gamb_ref)
        self.assertEqual(phib, phib_ref)
        self.assertEqual(psib, psib_ref)
        self.assertEqual(epsa, epsa_ref)

    def test_eraFal03(self):
        start_time = time.clock()
        self.ERFA.eraFal03(1)
        if self.show_perf:
            print(" ERFA Fal03      Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        erfaC.fal03(1)
        if self.show_perf:
            print(" ERFA Fal03      Astropy {0:15.15f} seconds".format((time.clock() - start_time)))
        for i in range(-10, 10):
            el = self.ERFA.eraFal03(i)
            el_ref = erfaC.fal03(i)
            self.assertEqual(el, el_ref)

    def test_eraFaf03(self):
        start_time = time.clock()
        self.ERFA.eraFaf03(1)
        if self.show_perf:
            print(" ERFA Faf03      Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        erfaC.faf03(1)
        if self.show_perf:
            print(" ERFA Faf03      Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        for i in range(-10, 10):
            el = self.ERFA.eraFaf03(i)
            el_ref = erfaC.faf03(i)
            self.assertEqual(el, el_ref)

    def test_eraFaom03(self):
        start_time = time.clock()
        self.ERFA.eraFaom03(1)
        if self.show_perf:
            print(" ERFA Faom03     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        erfaC.faom03(1)
        if self.show_perf:
            print(" ERFA Faom03     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        for i in range(-10, 10):
            el_ref = erfaC.faom03(i)
            el = self.ERFA.eraFaom03(i)
            self.assertEqual(el, el_ref)

    def test_eraNut00a(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)

        start_time = time.clock()
        dp, de = self.ERFA.eraNut00a(date1, date2)
        if self.show_perf:
            print(" ERFA Nut00a     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        dp_ref, de_ref = erfaC.nut00a(date1, date2)
        if self.show_perf:
            print(" ERFA Nut00a     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(dp, dp_ref)
        self.assertEqual(de, de_ref)

    def test_eraNut06a(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)

        start_time = time.clock()
        dp, de = self.ERFA.eraNut06a(date1, date2)
        if self.show_perf:
            print(" ERFA Nut06a     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        dp_ref, de_ref = erfaC.nut06a(date1, date2)
        if self.show_perf:
            print(" ERFA Nut06a     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(dp, dp_ref)
        self.assertEqual(de, de_ref)

    def test_eraPnm06a(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)

        start_time = time.clock()
        rnpb = self.ERFA.eraPnm06a(date1, date2)
        if self.show_perf:
            print(" ERFA Pnm06a     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        rnpb_ref = erfaC.pnm06a(date1, date2)
        if self.show_perf:
            print(" ERFA Pnm06a     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(rnpb[0][0], rnpb_ref[0][0])
        self.assertEqual(rnpb[0][1], rnpb_ref[0][1])
        self.assertEqual(rnpb[0][2], rnpb_ref[0][2])
        self.assertEqual(rnpb[1][0], rnpb_ref[1][0])
        self.assertEqual(rnpb[1][1], rnpb_ref[1][1])
        self.assertEqual(rnpb[1][2], rnpb_ref[1][2])
        self.assertEqual(rnpb[2][0], rnpb_ref[2][0])
        self.assertEqual(rnpb[2][1], rnpb_ref[2][1])
        self.assertEqual(rnpb[2][2], rnpb_ref[2][2])

    def test_eraBpn2xy(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        rnpb = self.ERFA.eraPnm06a(date1, date2)

        start_time = time.clock()
        x, y = self.ERFA.eraBpn2xy(rnpb)
        if self.show_perf:
            print(" ERFA Bpn2xy     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        x_ref, y_ref = erfaC.bpn2xy(rnpb)
        if self.show_perf:
            print(" ERFA Bpn2xy     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(x, x_ref)
        self.assertEqual(y, y_ref)

    def test_eraS06(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        rnpb = self.ERFA.eraPnm06a(date1, date2)
        x, y = self.ERFA.eraBpn2xy(rnpb)

        start_time = time.clock()
        val = self.ERFA.eraS06(date1, date2, x, y)
        if self.show_perf:
            print(" ERFA S06        Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        val_ref = erfaC.s06(date1, date2, x, y)
        if self.show_perf:
            print(" ERFA S06        Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(val, val_ref)

    def test_eraApci(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        ok, ehpv, ebpv = self.ERFA.eraEpv00(date1, date2)
        rnpb = self.ERFA.eraPnm06a(date1, date2)
        x, y = self.ERFA.eraBpn2xy(rnpb)
        s = self.ERFA.eraS06(date1, date2, x, y)

        start_time = time.clock()
        self.ERFA.eraApci(date1, date2, ebpv,  ehpv[0], x, y, s)
        if self.show_perf:
            print(" ERFA Apci       Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        astrom_ref = erfaC.apci(date1, date2, ebpv,  ehpv[0], x, y, s)
        if self.show_perf:
            print(" ERFA Apci       Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(astrom_ref[()][6][0][0], self.ERFA.astrom.bpn[0][0])
        self.assertEqual(astrom_ref[()][6][0][1], self.ERFA.astrom.bpn[0][1])
        self.assertEqual(astrom_ref[()][6][0][2], self.ERFA.astrom.bpn[0][2])
        self.assertEqual(astrom_ref[()][6][1][0], self.ERFA.astrom.bpn[1][0])
        self.assertEqual(astrom_ref[()][6][1][1], self.ERFA.astrom.bpn[1][1])
        self.assertEqual(astrom_ref[()][6][1][2], self.ERFA.astrom.bpn[1][2])
        self.assertEqual(astrom_ref[()][6][2][0], self.ERFA.astrom.bpn[2][0])
        self.assertEqual(astrom_ref[()][6][2][1], self.ERFA.astrom.bpn[2][1])
        self.assertEqual(astrom_ref[()][6][2][2], self.ERFA.astrom.bpn[2][2])

    def test_eraEors(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        ok, ehpv, ebpv = self.ERFA.eraEpv00(date1, date2)
        rnpb = self.ERFA.eraPnm06a(date1, date2)
        x, y = self.ERFA.eraBpn2xy(rnpb)
        s = self.ERFA.eraS06(date1, date2, x, y)
        self.ERFA.eraApci(date1, date2, ebpv,  ehpv[0], x, y, s)

        start_time = time.clock()
        eo = self.ERFA.eraEors(rnpb, s)
        if self.show_perf:
            print(" ERFA Eors       Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        eo_ref = erfaC.eors(rnpb, s)
        if self.show_perf:
            print(" ERFA Eors       Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(eo, eo_ref)

    def test_eraApci13(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)

        start_time = time.clock()
        eo = self.ERFA.eraApci13(date1, date2)
        if self.show_perf:
            print(" ERFA Apci13     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        astrom_ref, eo_ref = erfaC.apci13(date1, date2)
        if self.show_perf:
            print(" ERFA Apci13     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(astrom_ref[()][0], self.ERFA.astrom.pmt)
        self.assertEqual(astrom_ref[()][1][0], self.ERFA.astrom.eb[0])
        self.assertEqual(astrom_ref[()][1][1], self.ERFA.astrom.eb[1])
        self.assertEqual(astrom_ref[()][1][2], self.ERFA.astrom.eb[2])
        self.assertEqual(astrom_ref[()][2][0], self.ERFA.astrom.eh[0])
        self.assertEqual(astrom_ref[()][2][1], self.ERFA.astrom.eh[1])
        self.assertEqual(astrom_ref[()][2][2], self.ERFA.astrom.eh[2])
        self.assertEqual(astrom_ref[()][3], self.ERFA.astrom.em)
        self.assertEqual(astrom_ref[()][4][0], self.ERFA.astrom.v[0])
        self.assertEqual(astrom_ref[()][4][1], self.ERFA.astrom.v[1])
        self.assertEqual(astrom_ref[()][4][2], self.ERFA.astrom.v[2])
        self.assertEqual(astrom_ref[()][5], self.ERFA.astrom.bml)
        self.assertEqual(astrom_ref[()][6][0][0], self.ERFA.astrom.bpn[0][0])
        self.assertEqual(astrom_ref[()][6][0][1], self.ERFA.astrom.bpn[0][1])
        self.assertEqual(astrom_ref[()][6][0][2], self.ERFA.astrom.bpn[0][2])
        self.assertEqual(astrom_ref[()][6][1][0], self.ERFA.astrom.bpn[1][0])
        self.assertEqual(astrom_ref[()][6][1][1], self.ERFA.astrom.bpn[1][1])
        self.assertEqual(astrom_ref[()][6][1][2], self.ERFA.astrom.bpn[1][2])
        self.assertEqual(astrom_ref[()][6][2][0], self.ERFA.astrom.bpn[2][0])
        self.assertEqual(astrom_ref[()][6][2][1], self.ERFA.astrom.bpn[2][1])
        self.assertEqual(astrom_ref[()][6][2][2], self.ERFA.astrom.bpn[2][2])
        # self.assertAlmostEqual(astrom_ref[()][7], self.ERFA.astrom.along)
        self.assertAlmostEqual(astrom_ref[()][8], self.ERFA.astrom.phi)
        self.assertAlmostEqual(astrom_ref[()][9], self.ERFA.astrom.xpl)
        self.assertAlmostEqual(astrom_ref[()][10], self.ERFA.astrom.ypl)
        self.assertAlmostEqual(astrom_ref[()][11], self.ERFA.astrom.sphi)
        # self.assertAlmostEqual(astrom_ref[()][12], self.ERFA.astrom.cphi)
        self.assertAlmostEqual(astrom_ref[()][13], self.ERFA.astrom.diurab)
        self.assertAlmostEqual(astrom_ref[()][14], self.ERFA.astrom.eral)
        self.assertAlmostEqual(astrom_ref[()][15], self.ERFA.astrom.refa)
        self.assertAlmostEqual(astrom_ref[()][16], self.ERFA.astrom.refb)
        self.assertAlmostEqual(eo_ref, eo)

    def test_eraPmpx(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        self.ERFA.eraApci13(date1, date2)
        rc = 3.14
        dc = 0.5
        pr = 0
        pd = 0
        px = 0
        rv = 0

        start_time = time.clock()
        pco = self.ERFA.eraPmpx(rc, dc, pr, pd, px, rv, self.ERFA.astrom.pmt, self.ERFA.astrom.eb)
        if self.show_perf:
            print(" ERFA Pmpx       Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        pco_ref = erfaC.pmpx(rc, dc, pr, pd, px, rv, self.ERFA.astrom.pmt, self.ERFA.astrom.eb)
        if self.show_perf:
            print(" ERFA Pmpx       Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(pco[0], pco_ref[0])
        self.assertEqual(pco[1], pco_ref[1])
        self.assertEqual(pco[2], pco_ref[2])

    def test_eraLdsun(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        self.ERFA.eraApci13(date1, date2)
        rc = 3.14
        dc = 0.5
        pr = 0
        pd = 0
        px = 0
        rv = 0
        pco = self.ERFA.eraPmpx(rc, dc, pr, pd, px, rv, self.ERFA.astrom.pmt, self.ERFA.astrom.eb)

        start_time = time.clock()
        pnat = self.ERFA.eraLdsun(pco, self.ERFA.astrom.eh, self.ERFA.astrom.em)
        if self.show_perf:
            print(" ERFA Ldsun      Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        pnat_ref = erfaC.ldsun(pco, self.ERFA.astrom.eh, self.ERFA.astrom.em)
        if self.show_perf:
            print(" ERFA Ldsun      Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(pnat[0], pnat_ref[0])
        self.assertEqual(pnat[1], pnat_ref[1])
        self.assertEqual(pnat[2], pnat_ref[2])

    def test_eraAb(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        self.ERFA.eraApci13(date1, date2)
        rc = 3.14
        dc = 0.5
        pr = 0
        pd = 0
        px = 0
        rv = 0
        pco = self.ERFA.eraPmpx(rc, dc, pr, pd, px, rv, self.ERFA.astrom.pmt, self.ERFA.astrom.eb)
        pnat = self.ERFA.eraLdsun(pco, self.ERFA.astrom.eh, self.ERFA.astrom.em)

        start_time = time.clock()
        ppr = self.ERFA.eraAb(pnat, self.ERFA.astrom.v, self.ERFA.astrom.em, self.ERFA.astrom.bml)
        if self.show_perf:
            print(" ERFA Ab         Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        ppr_ref = erfaC.ab(pnat, self.ERFA.astrom.v, self.ERFA.astrom.em, self.ERFA.astrom.bml)
        if self.show_perf:
            print(" ERFA Ab         Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(ppr[0], ppr_ref[0])
        self.assertEqual(ppr[1], ppr_ref[1])
        self.assertEqual(ppr[2], ppr_ref[2])

    def test_eraAtci13(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        rc = 3.14
        dc = 0.5
        pr = 0
        pd = 0
        px = 0
        rv = 0

        start_time = time.clock()
        ri, di, eo = self.ERFA.eraAtci13(rc, dc, pr, pd, px, rv, date1, date2)
        if self.show_perf:
            print(" ERFA Atci13     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        ri_ref, di_ref, eo_ref = erfaC.atci13(rc, dc, pr, pd, px, rv, date1, date2)
        if self.show_perf:
            print(" ERFA Atci13     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(ri, ri_ref)
        self.assertEqual(di, di_ref)
        self.assertEqual(eo, eo_ref)

    def test_eraAtic13(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        ri = 03.84027 * self.ERFA.ERFA_D2PI / 24
        di = 61.3768 * self.ERFA.ERFA_D2PI / 360

        start_time = time.clock()
        rc, dc, eo = self.ERFA.eraAtic13(ri, di, date1, date2)
        if self.show_perf:
            print(" ERFA Atic13     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        rc_ref, dc_ref, eo_ref = erfaC.atic13(ri, di, date1, date2)
        if self.show_perf:
            print(" ERFA Atic13     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(rc, rc_ref)
        self.assertEqual(dc, dc_ref)
        self.assertEqual(eo, eo_ref)

    def test_eraAtioq(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        r = 1.5
        d = 2.0
        eo = self.ERFA.eraApci13(date1, date2)
        astrom_ref, eo_ref = erfaC.apci13(date1, date2)

        start_time = time.clock()
        aob, zob, hob, dob, rob = self.ERFA.eraAtioq(r, d)
        if self.show_perf:
            print(" ERFA Atioq      Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        aob_ref, zob_ref, hob_ref, dob_ref, rob_ref = erfaC.atioq(r, d, astrom_ref)
        if self.show_perf:
            print(" ERFA Atioq      Astropy {0:15.15f} seconds".format((time.clock() - start_time)))
        self.assertEqual(aob, aob_ref)
        self.assertEqual(zob, zob_ref)
        self.assertEqual(hob, hob_ref)
        self.assertEqual(dob, dob_ref)
        self.assertEqual(rob, rob_ref)

    def test_eraUtctai(self):
        ok, utc1, utc2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)

        start_time = time.clock()
        ok, tai1, tai2 = self.ERFA.eraUtctai(utc1, utc2)
        if self.show_perf:
            print(" ERFA Utctai     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        tai1_ref, tai2_ref = erfaC.utctai(utc1, utc2)
        if self.show_perf:
            print(" ERFA Utctai     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(ok, 0)
        self.assertEqual(tai1, tai1_ref)
        self.assertEqual(tai2, tai2_ref)

    def test_eraUtcutl(self):
        ok, utc1, utc2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        dt = 30

        start_time = time.clock()
        ok, ut11, ut12 = self.ERFA.eraUtcut1(utc1, utc2, dt)
        if self.show_perf:
            print(" ERFA Utcutl     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        ut11_ref, ut12_ref = erfaC.utcut1(utc1, utc2, dt)
        if self.show_perf:
            print(" ERFA Utcutl     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(ok, 0)
        self.assertEqual(ut11, ut11_ref)
        self.assertEqual(ut12, ut12_ref)

    def test_eraRefco(self):
        phpa = 1000
        tc = 20
        rh = 0.8
        wl = 0.57

        start_time = time.clock()
        refa, refb = self.ERFA.eraRefco(phpa, tc, rh, wl)
        if self.show_perf:
            print(" ERFA Refco      Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        refa_ref, refb_ref = erfaC.refco(phpa, tc, rh, wl)
        if self.show_perf:
            print(" ERFA Refco      Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(refa, refa_ref)
        self.assertEqual(refb, refb_ref)

    def test_eraApco13(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        elong = 11.0 * self.ERFA.ERFA_DD2R
        phi = 49.0 * self.ERFA.ERFA_DD2R
        hm = 583.0
        xp = 0
        yp = 0
        j, dut1 = self.ERFA.eraDat(self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, 0)
        phpa = 1000
        tc = 20
        rh = 0.8
        wl = 0.57

        start_time = time.clock()
        j, eo = self.ERFA.eraApco13(date1, date2, dut1, elong, phi, hm, xp, yp, phpa, tc, rh, wl)
        if self.show_perf:
            print(" ERFA Apco13     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        astrom_ref, eo_ref = erfaC.apco13(date1, date2, dut1, elong, phi, hm, xp, yp, phpa, tc, rh, wl)
        if self.show_perf:
            print(" ERFA Apco13     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(astrom_ref[()][0], self.ERFA.astrom.pmt)
        self.assertEqual(astrom_ref[()][1][0], self.ERFA.astrom.eb[0])
        self.assertEqual(astrom_ref[()][1][1], self.ERFA.astrom.eb[1])
        self.assertEqual(astrom_ref[()][1][2], self.ERFA.astrom.eb[2])
        self.assertEqual(astrom_ref[()][2][0], self.ERFA.astrom.eh[0])
        self.assertEqual(astrom_ref[()][2][1], self.ERFA.astrom.eh[1])
        self.assertEqual(astrom_ref[()][2][2], self.ERFA.astrom.eh[2])
        self.assertEqual(astrom_ref[()][3], self.ERFA.astrom.em)
        self.assertEqual(astrom_ref[()][4][0], self.ERFA.astrom.v[0])
        self.assertEqual(astrom_ref[()][4][1], self.ERFA.astrom.v[1])
        self.assertEqual(astrom_ref[()][4][2], self.ERFA.astrom.v[2])
        self.assertEqual(astrom_ref[()][5], self.ERFA.astrom.bml)
        self.assertEqual(astrom_ref[()][6][0][0], self.ERFA.astrom.bpn[0][0])
        self.assertEqual(astrom_ref[()][6][0][1], self.ERFA.astrom.bpn[0][1])
        self.assertEqual(astrom_ref[()][6][0][2], self.ERFA.astrom.bpn[0][2])
        self.assertEqual(astrom_ref[()][6][1][0], self.ERFA.astrom.bpn[1][0])
        self.assertEqual(astrom_ref[()][6][1][1], self.ERFA.astrom.bpn[1][1])
        self.assertEqual(astrom_ref[()][6][1][2], self.ERFA.astrom.bpn[1][2])
        self.assertEqual(astrom_ref[()][6][2][0], self.ERFA.astrom.bpn[2][0])
        self.assertEqual(astrom_ref[()][6][2][1], self.ERFA.astrom.bpn[2][1])
        self.assertEqual(astrom_ref[()][6][2][2], self.ERFA.astrom.bpn[2][2])
        self.assertAlmostEqual(astrom_ref[()][7], self.ERFA.astrom.along)
        self.assertAlmostEqual(astrom_ref[()][8], self.ERFA.astrom.phi)
        self.assertAlmostEqual(astrom_ref[()][9], self.ERFA.astrom.xpl)
        self.assertAlmostEqual(astrom_ref[()][10], self.ERFA.astrom.ypl)
        self.assertAlmostEqual(astrom_ref[()][11], self.ERFA.astrom.sphi)
        self.assertAlmostEqual(astrom_ref[()][12], self.ERFA.astrom.cphi)
        self.assertAlmostEqual(astrom_ref[()][13], self.ERFA.astrom.diurab)
        self.assertAlmostEqual(astrom_ref[()][14], self.ERFA.astrom.eral)
        self.assertAlmostEqual(astrom_ref[()][15], self.ERFA.astrom.refa)
        self.assertAlmostEqual(astrom_ref[()][16], self.ERFA.astrom.refb)
        self.assertAlmostEqual(eo_ref, eo)

    def test_eraAtoc13(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        elong = 11.0 * self.ERFA.ERFA_DD2R
        phi = 49.0 * self.ERFA.ERFA_DD2R
        hm = 583.0
        xp = 0
        yp = 0
        j, dut1 = self.ERFA.eraDat(self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, 0)
        phpa = 1000
        tc = 20
        rh = 0.8
        wl = 0.57
        ob1 = 3.14
        ob2 = 0.5
        type_ERA = 'A'

        start_time = time.clock()
        j, rc, dc = self.ERFA.eraAtoc13(type_ERA, ob1, ob2, date1, date2, dut1, elong, phi, hm, xp, yp, phpa, tc, rh, wl)
        if self.show_perf:
            print(" ERFA Atoc13     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        rc_ref, dc_ref = erfaC.atoc13(type_ERA, ob1, ob2, date1, date2, dut1, elong, phi, hm, xp, yp, phpa, tc, rh, wl)
        if self.show_perf:
            print(" ERFA Atoc13     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))

        self.assertEqual(rc, rc_ref)
        self.assertEqual(dc, dc_ref)
        self.assertEqual(ok, 0)

    def test_eraAtco13(self):
        ok, date1, date2 = self.ERFA.eraDtf2d('UTC', self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, self.ts.tm_hour, self.ts.tm_min, self.ts.tm_sec)
        elong = 11.0 * self.ERFA.ERFA_DD2R
        phi = 49.0 * self.ERFA.ERFA_DD2R
        hm = 583.0
        xp = 0
        yp = 0
        j, dut1 = self.ERFA.eraDat(self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday, 0)
        phpa = 1000
        tc = 20
        rh = 0.8
        wl = 0.57
        rc = 20 * self.ERFA.ERFA_DD2R * 24 / 360
        dc = 0 * self.ERFA.ERFA_DD2R
        pr = 0
        pd = 0
        px = 0
        rv = 0

        start_time = time.clock()
        ok, aob, zob, hob, dob, rob, eo = self.ERFA.eraAtco13(rc, dc, pr, pd, px, rv, date1, date2, dut1, elong, phi, hm, xp, yp, phpa, tc, rh, wl)
        if self.show_perf:
            print(" ERFA Apco13     Python  {0:15.15f} seconds".format((time.clock() - start_time)))

        start_time = time.clock()
        aob_ref, zob_ref, hob_ref, dob_ref, rob_ref, eo_ref = erfaC.atco13(rc, dc, pr, pd, px, rv, date1, date2, dut1, elong, phi, hm, xp, yp, phpa, tc, rh, wl)
        if self.show_perf:
            print(" ERFA Apco13     Astropy {0:15.15f} seconds".format((time.clock() - start_time)))
        self.assertEqual(ok, 0)
        self.assertEqual(aob, aob_ref)
        self.assertEqual(zob, zob_ref)
        self.assertEqual(hob, hob_ref)
        self.assertEqual(dob, dob_ref)
        self.assertEqual(rob, rob_ref)
        self.assertEqual(eo, eo_ref)

