#!/usr/bin/python3
# Bandpass, gain and flux calibration
# https://casa.nrao.edu/docs/TaskRef/fixvis-task.html
# https://casa.nrao.edu/docs/TaskRef/clearcal-task.html
# https://casa.nrao.edu/docs/TaskRef/setjy-task.html
# https://casa.nrao.edu/docs/TaskRef/bandpass-task.html
# https://casa.nrao.edu/docs/TaskRef/gaincal-task.html
# https://casa.nrao.edu/docs/TaskRef/fluxscale-task.html
# https://casa.nrao.edu/docs/TaskRef/applycal-task.html

from os import F_OK
from taskinit import *
from tasks import *

import argparse
import casac
import os

## -- global parameters for script --
DEBUG = False
VERBOSE = False
flux_calibrators = {'J0408-6545': [17.1, 0, 0, 0],
                    'J1939-6342': 'Stevens-Reynolds 2016',
                    'J1331+3030': 'Perley-Butler 2013',
                    }
## -- global parameters for script --


## -- utility functions --
def _get_prefix(msfile):
    """Extract basename of MS as prefix for new namings"""
    return os.path.splitext(os.path.basename(msfile))[0]


def _str2list(string_):
    list_ = [str_.strip() for str_ in string_.split(',')]
    return list(set(list_))


def _list2str(list_):
    if len(list_) > 0:
        return ','.join(list(set(list_)))
    else:
        return ''


def _print_msg(msg):
    """
    Intended for status messages within CASA during calibration.
    Extra padding to make it stand out amongst all the other CASA output
    """
    border = '#' * (23)
    msg_text = '\n{}'.format(border)
    msg_text += '### {} ###'.format(msg)
    msg_text += '{}\n'.format(border)
    print(msg_text)


def _run_cmd(cmd, table=None):
    if DEBUG or VERBOSE:
        print(cmd)
        if DEBUG:
            return None

    if table is not None:
        if os.access(table, F_OK):
            print('Deleting {} before cal\n'.format(table))
            rmtables(table)

    exec(cmd)


## -- utility functions --


def cli():
    usage = "%%prog [options] --msfile <filename.ms> -f <J...>"
    description = 'antenna based calibration corrections'

    parser = argparse.ArgumentParser(
            usage=usage,
            description=description,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='verbose output of casa commands while executing',
            )
    parser.add_argument(
            '--debug',
            action='store_true',
            help='output of casa commands for debugging without execution',
            )
    group = parser.add_argument_group(
            title="required arguments",
            description="arguments required by the script to run")
    group.add_argument(
            '--msfile',
            type=str,
            required=True,
            help='filename of measurement set',
            )
    flux_cals = flux_calibrators.keys()
    group.add_argument(
            '-f', '--fluxcal',
            type=str,
            required=True,
            help='flux calibrator: '
                 'suggested flux cals for MeerKAT {}'.format(flux_cals),
            )
    group = parser.add_argument_group(
            title="additional optional arguments",
            description="arguments only specified when necessary, logical defaults will be supplied")
    group.add_argument(
            '--fixvis',
            action='store_true',
            help='recalculates (u, v, w) and or phase centre',
            )
    group.add_argument(
            '--standard',
            type=str,
            help='standard flux model to apply, '
                 'leave blank to apply MeerKAT standard if available',
            )
    group.add_argument(
            '-b', '--bpcal',
            type=str,
            help='comma separated list of bandpass calibrator(s)',
            )
    group.add_argument(
            '-d', '--delaycal',
            type=str,
            help='comma separated list of delay calibrator(s)',
            )
    group.add_argument(
            '-g', '--gaincal',
            type=str,
            help='comma separated list of gain calibrator(s)',
            )
    group.add_argument(
            '-t', '--target',
            type=str,
            help='comma separated list of observation target(s)',
            )
    group.add_argument(
            '-r', '--ref-ant',
            type=str,
            default='',
            help='reference antenna full name, m0xx',
            )
    group.add_argument(
            '-c', '--ref-chans',
            type=str,
            default='',
            help='channels to use for preliminary gain calibration, \'spw:start_chan,end_chan\'',
            )
    group.add_argument(
            '--applycal',
            action='store_true',
            help='apply calibration solution to measurement set',
            )
    args = parser.parse_args()

    # set defaults for optional parameters
    if args.standard is None:
        if args.fluxcal in flux_cals:
            args.standard = flux_calibrators[args.fluxcal]
        else:
            msg = ("Not a standard MeerKAT calibrator, "
                   "please specify flux model: "
                   "--standard <flux_model> or --standard 'I, Q, U, V'")
            raise RuntimeError(msg)
    else:
        _eval_stokes = args.standard.split(',')
        if len(_eval_stokes) == 4:
            args.standard = [float(stokes) for stokes in _eval_stokes]

    if args.bpcal is None:
        args.bpcal = args.fluxcal
    if args.delaycal is None:
        args.delaycal = args.fluxcal
    if args.debug:
        global DEBUG
        DEBUG = True

    if args.verbose:
        global VERBOSE
        VERBOSE = True

    return args


def primary_calibrators(msfile,
                        f_cal,
                        bp_cal,
                        delay_cal,
                        ref_ant='',
                        prelim_gcal=False,
                        ref_chans='',
                        ):

    prefix = _get_prefix(msfile)
    _print_msg('Delay calibration')
    ktable = prefix + '.K'
    cmd = ("gaincal(vis='{}', caltable='{}', field='{}', "
           "gaintype='K', solint='inf', refant='{}', "
           "combine='scan,field', solnorm=False, minsnr=3.0, "
           "gaintable=[])".format(msfile, ktable, delay_cal, ref_ant))
    _run_cmd(cmd, table=ktable)
    gaintable_list=[ktable]

    if prelim_gcal:
        _print_msg('Preliminary gain calibration')
        gtable0 = prefix + '.G0'
        cmd = ("gaincal(vis='{}', caltable='{}', field='{}', "
               "gaintype='G', solint='inf', refant='{}', spw='{}', "
               "calmode='p', minsnr=3.0, solnorm=True, "
               "gaintable={})".format(
                    msfile, gtable0, f_cal, ref_ant, ref_chans, [ktable]))
        _run_cmd(cmd, table=gtable0)
        gaintable_list.insert(0, gtable0)

    _print_msg('Bandpass calibration')
    btable = prefix + '.B'
    cmd = ("bandpass(vis='{}', caltable='{}', field='{}', "
           "bandtype='B', solint='inf', refant='{}', "
           "combine='scan', solnorm=True, minsnr=3.0, "
           "gaintable={})".format(
               msfile, btable, bp_cal, ref_ant, gaintable_list))
    _run_cmd(cmd, table=btable)

    _print_msg('Gain calibration for flux calibrators')
    gtable = prefix + '.G'
    cmd = ("gaincal(vis='{}', caltable='{}', field='{}', "
           "gaintype='G', calmode='ap', solint='int', "
           "refant='{}', combine='spw', solnorm=False, minsnr=1.0, "
           "gaintable={})".format(
               msfile, gtable, f_cal, ref_ant, [btable, ktable]))
    _run_cmd(cmd, table=gtable)

    return [ktable, btable, gtable]


def secondary_calibrators(msfile,
                          ktable,
                          btable,
                          gtable,
                          g_cal,
                          ref_ant='',
                          ):

    prefix = _get_prefix(msfile)
    _print_msg('Gain calibration for remaining calibrators')
    cmd = ("gaincal(vis='{}', caltable='{}', field='{}', "
           "gaintype='G', calmode='ap', solint='int', refant='{}', "
           "combine='spw', solnorm=False, minsnr=1.0, append=True, "
           "gaintable={})".format(
               msfile, gtable, g_cal, ref_ant, [btable, ktable]))
    _run_cmd(cmd)

    return gtable


def flux_calibration(msfile,
                     ftable,
                     gtable,
                     f_cal,
                     g_cal,
                     ):
    prefix = _get_prefix(msfile)
    _print_msg('Fluxscale calibration for secondary cal')
    ftable = prefix + '.flux'
    cmd = ("fluxscale(vis='{}', caltable='{}', fluxtable='{}', "
           "reference='{}', transfer='{}')".format(
               msfile, gtable, ftable, f_cal, g_cal))
    _run_cmd(cmd, table=ftable)
    return ftable


def apply_calibration(msfile,
                      cals,
                      gaintables,
                      g_cal,
                      bp_cal,
                      delay_cal,
                      targets=None,
                      ):

    _print_msg('Apply calibration results')
    if not DEBUG:
        clearstat()

    def _build_cmd(msfile, gaintables, target, g_cal, bp_cal, delay_cal):
        cmd = ("applycal(vis='{}', field ='{}', gaintable={}, gainfield={}, "
               "interp=['', 'nearest', ''], calwt=False, "
               "applymode='calflag')".format(
                    msfile, target, gaintables, [g_cal, bp_cal, delay_cal]))
        return cmd

    # apply calibration to calibrators
    for cal in cals:
        cmd = _build_cmd(msfile,
                         gaintables,
                         cal,
                         cal,
                         bp_cal,
                         delay_cal)
        _run_cmd(cmd)

    # apply calibration to targets
    if targets is not None:
        for tgt in targets:
            cmd = _build_cmd(msfile,
                             gaintables,
                             tgt,
                             g_cal,
                             bp_cal,
                             delay_cal)
            _run_cmd(cmd)


def calibrate(msfile,
              f_cal,
              bp_cal,
              delay_cal,
              g_cal=None,
              ref_ant='',
              standard=None,
              prelim_gcal=False,
              ref_chans='',
              ):

    _print_msg('Clear existing calibration results')
    cmd = "clearcal('{}')".format(msfile)
    _run_cmd(cmd)

    ktable = ''
    btable = ''
    gtable = ''
    ftable = ''

    # To convert correlation coefficients to absolute flux densities
    _print_msg('Apply flux model to flux calibrator')
    if type(standard) is list:
        cmd = ("setjy(vis='{}', field='{}', "
               "scalebychan=True, standard='manual', "
               "fluxdensity={})".format(
                      msfile, f_cal, standard))
    else:
        cmd = ("setjy(vis='{}', field='{}', "
              "scalebychan=True, "
              "standard='{}', fluxdensity=-1)".format(
                      msfile, f_cal, standard))
    _run_cmd(cmd)

    [ktable, btable, gtable] = primary_calibrators(msfile,
                                                   f_cal,
                                                   bp_cal,
                                                   delay_cal,
                                                   ref_ant=ref_ant,
                                                   prelim_gcal=prelim_gcal,
                                                   ref_chans=ref_chans,
                                                   )
    msg = lambda str_ : 'No {} solution, exiting...'.format(str_)
    if not os.path.isdir(ktable) and not DEBUG:
        raise RuntimeError(msg('delay'))
    if not os.path.isdir(btable) and not DEBUG:
        raise RuntimeError(msg('bandpass'))
    if not os.path.isdir(gtable) and not DEBUG:
        raise RuntimeError(msg('gain'))

    cal_tables = [gtable, btable, ktable]

    cals = _str2list(bp_cal)
    f_cals = _str2list(f_cal)
    for cal in cals:
        if cal in f_cals:
            cals.remove(cal)
    if g_cal is not None:
        cals += _str2list(g_cal)
    g_cal = _list2str(cals)
    if g_cal:
        gtable = secondary_calibrators(msfile,
                                       ktable,
                                       btable,
                                       gtable,
                                       g_cal=g_cal,
                                       ref_ant=ref_ant,
                                       )

        ftable = flux_calibration(msfile,
                                  ftable,
                                  gtable,
                                  f_cal,
                                  g_cal)
        if not os.path.isdir(ftable) and not DEBUG:
            raise RuntimeError(msg('flux'))
        cal_tables = [ftable, btable, ktable]

    return cal_tables


if __name__ == '__main__':
    args = cli()

    msfile = args.msfile
    f_cal = args.fluxcal
    bp_cal = args.bpcal
    delay_cal = args.delaycal
    g_cal = args.gaincal
    target = args.target
    ref_ant = args.ref_ant

    _print_msg("Processing with CASA")
    print("  msfile='{}'".format(msfile))
    print("  f_cal='{}'".format(f_cal))
    print("  bp_cal='{}'".format(bp_cal))
    print("  delay_cal='{}'".format(delay_cal))
    if g_cal is not None:
        print("  g_cal='{}'".format(g_cal))
    if target is not None:
        print("  target='{}'".format(target))
    if ref_ant is not None:
        print("  ref_ant='{}'".format(ref_ant))

    if args.fixvis:
        prefix = _get_prefix(msfile)
        _print_msg('Correct phase center with fixvis')
        cmd = "fixvis(vis='{}', outputvis='{}')".format(
                msfile, prefix+'_fixvis.ms')
        _run_cmd(cmd)
        msfile = prefix+'_fixvis.ms'
        print('Phase center correction')
        print("  msfile='{}'".format(msfile))

    cal_tables = calibrate(msfile,
                           f_cal,
                           bp_cal,
                           delay_cal,
                           g_cal=g_cal,
                           ref_ant=ref_ant,
                           standard=args.standard,
                           prelim_gcal=True,
                           ref_chans=args.ref_chans,
                           )

    if args.applycal:
        cals = _str2list(','.join((f_cal, bp_cal, g_cal)))
        if target is not None:
            targets = _str2list(target)
            apply_calibration(msfile,
                              cals,
                              cal_tables,
                              g_cal,
                              bp_cal,
                              delay_cal,
                              targets)

# -fin-
