#!/usr/bin/python3
# Automated flagging for shadowing, elevations below 15 degrees and extreme outliers
# https://casa.nrao.edu/docs/TaskRef/flagdata-task.html

from taskinit import *
from tasks import *

import argparse
import casac


def cli():
    usage = "%%prog [options] --msfile <filename>"
    description = 'Automated flagging of measurement set'

    parser = argparse.ArgumentParser(
            usage=usage,
            description=description)
    parser.add_argument(
            '--msfile',
            type=str,
            required=True,
            help='Filename of measurement set',
            )
    parser.add_argument(
            '--zeros',
            action='store_true',
            help='Clip zeros-value data',
            )
    parser.add_argument(
            '--bp',
            action='store_true',
            help='Flag out bandpass edge frequencies',
            )
    parser.add_argument(
            '--mw',
            action='store_true',
            help='Flag Milky Way',
            )
    parser.add_argument(
            '--lband',
            action='store_true',
            help='Flag out known environmental RFI for L-band',
            )
    parser.add_argument(
            '--gps',
            action='store_true',
            help='Flag out GPS L1: 1565-1585, L2: 1217-1237,'
                 'L3: 1375-1387, L5: 1166-1186 [MHz]',
            )
    parser.add_argument(
            '--glonass',
            action='store_true',
            help='Flag out GLONASS L1: 1592-1610, L2: 1242-1249 [MHz]',
            )
    parser.add_argument(
            '--galileo',
            action='store_true',
            help='Flag out galileo 1191-1217, 1260-1300 [MHz]',
            )
    parser.add_argument(
            '--afristar',
            action='store_true',
            help='Flag out Afristar 1453-1490 [MHz]',
            )
    parser.add_argument(
            '--iridium',
            action='store_true',
            help='Flag out IRIDIUM 1616-1626 [MHz]',
            )
    parser.add_argument(
            '--inmarsat',
            action='store_true',
            help='Flag out Inmarsat 1526-1554 [MHz]',
            )
    return parser.parse_args()


def basic_flagging(msfile,
                   zeros=False):  # clip zero value data
    flagdata(vis=msfile,
             mode='shadow',
             flagbackup=False)
    flagdata(vis=msfile,
             mode='elevation',
             lowerlimit=15,
             flagbackup=False)
    flagdata(vis=msfile,
             mode='clip',
             clipminmax=[1e-5, 1000.0],
             flagbackup=False)
    if zeros:
        flagdata(vis=msfile,
                 mode='clip',
                 field='',
                 clipzeros=True,
                 flagbackup=False)


# flag bandpass edges
def bp_edges_flagging(msfile,
                      band='l'):
    if str.lower(band) == 'l':
        flagdata(vis=msfile,
                 mode='manual',
                 spw='*:856MHZ~880MHZ;1658MHZ~1800MHZ',
                 flagbackup=False)


# flag Milky Way
def mw_flagging(msfile):
    flagdata(vis=msfile,
             mode='manual',
             spw='*:1420.0MHZ~1421.3MHZ',
             flagbackup=False)


# flag out known satellite RFI frequencies
def lband_env_flagging(msfile,
                       ligo_freq=None):
    # flag out aviation channels
    if ligo_freq is None:
        ligo_freq = '*:1080MHZ~1095MHZ'
    flagdata(vis=msfile,
             mode='manual',
             spw=ligo_freq,
             flagbackup=False)
    # GSM
    flagdata(vis=msfile,
             mode='manual',
             spw='*:900MHZ~915MHZ;925MHZ~960MHZ',
             flagbackup=False)
    # Alkantpan
    flagdata(vis=msfile,
             mode='manual',
             spw='*:1600MHZ',
             flagbackup=False)


# flag out known satellite RFI frequencies
def sat_rfi_flagging(msfile,
                     gps=False,
                     glonass=False,
                     galileo=False,
                     afristar=False,
                     iridium=False,
                     inmarsat=False):
    if gps:  # GPS
        flagdata(vis=msfile,
                 mode='manual',
                 spw='*:1565MHZ~1585MHZ;1217MHZ~1237MHZ;1375MHZ~1387MHZ;1166MHZ~1186MHZ',
                 flagbackup=False)
    if glonass:  # GLONASS
        flagdata(vis=msfile,
                 mode='manual',
                 spw='*:1592MHZ~1610MHZ;1242MHZ~1249MHZ',
                 flagbackup=False)
    if galileo:  # Galileo
        flagdata(vis=msfile,
                 mode='manual',
                 spw='*:1191MHZ~1217MHZ;1260MHZ~1300MHZ',
                 flagbackup=False)
    if afristar:  # Afristar
        flagdata(vis=msfile,
                 mode='manual',
                 spw='*:1453MHZ~1490MHZ',
                 flagbackup=False)
    if iridium:  # IRIDIUM
        flagdata(vis=msfile,
                 mode='manual',
                 spw='*:1616MHZ~1626MHZ',
                 flagbackup=False)
    if inmarsat:  # Inmarsat
        flagdata(vis=msfile,
                 mode='manual',
                 spw='*:1526MHZ~1554MHZ',
                 flagbackup=False)


if __name__ == '__main__':
    args = cli()
    basic_flagging(args.msfile,
                   zeros=args.zeros)
    if args.bp:
        bp_edges_flagging(args.msfile)
    if args.mw:
        mw_flagging(args.msfile)
    if args.lband:
        lband_env_flagging(args.msfile)
    sat_rfi_flagging(args.msfile,
                 gps=args.gps,
                 glonass=args.glonass,
                 galileo=args.galileo,
                 afristar=args.afristar,
                 iridium=args.iridium)

# -fin-
