#!/usr/bin/python3
# https://casa.nrao.edu/docs/TaskRef/plotcal-task.html

from os import F_OK
from taskinit import *
from tasks import *

import argparse
import casac
import os


def print_msg(msg):
    msg_text = '\n###\t{}\t###\n'.format(msg)
    print(msg_text)


def cli():
    usage = "%%prog [options]"
    description = 'antenna based calibration solutions'

    parser = argparse.ArgumentParser(
             usage=usage,
             description=description,
             formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
            '--delaycal',
            dest='ktable',
            metavar='ktable',
            type=str,
            help="CASA delay calibration solution table name, 'K'",
            )
    parser.add_argument(
            '--prelim',
            dest='gtable0',
            metavar='gtable0',
            type=str,
            help="CASA preliminary gain calibration solution table name",
            )
    parser.add_argument(
            '--bpcal',
            dest='btable',
            metavar='btable',
            type=str,
            help="CASA bandpass calibration solution table name, 'B'",
            )
    parser.add_argument(
            '--gaincal',
            dest='gtable',
            metavar='gtable',
            type=str,
            help="CASA gain/phase calibration table name, 'G'",
            )
    parser.add_argument(
            '--primary',
            type=str,
            help="comma separated list of primary calibrators "
                 "for gain calibration solution displays",
            )
    parser.add_argument(
            '--secondary',
            type=str,
            help="comma separated list of gain calibrators "
                 "for gain calibration solution displays",
            )
    parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='display calibration results',
            )
    return parser.parse_args()


if __name__ == '__main__':
    args = cli()

    if args.ktable:
        print_msg("Delays after calibration should be no more than "
                  "a few nanoseconds and spread around/close to zero.")
        plotcal(caltable=args.ktable,
                xaxis='antenna', yaxis='delay',
                showgui=args.verbose, figfile='delay_solutions.png')

    if args.gtable0:
        print_msg("Through away phase calibration to stabilize "
                  "time varying components")
        plotcal(caltable=args.gtable0,
                xaxis='time', yaxis='phase',
                plotrange=[-1, -1, -180, 180],
                showgui=args.verbose, figfile='prelim_phase_solutions.png')

    if args.btable:
        print_msg("Phase solutions should be around 0")
        plotcal(caltable=args.btable,
                xaxis='chan', yaxis='phase',
                showgui=args.verbose, figfile='bandpass_phase_solutions.png')
        print_msg("Passband amp around 1. and consistent with bandpass shape.")
        plotcal(caltable=args.btable,
                xaxis='chan', yaxis='amp',
                showgui=args.verbose, figfile='bandpass_amp_solutions.png')

    if args.gtable:
        print_msg("Phase solutions should be in a straight line")
        if args.primary:
            plotcal(caltable=args.gtable,
                    xaxis='time', yaxis='phase',
                    field=args.primary,
                    plotrange=[-1, -1, -180, 180],
                    showgui=args.verbose,
                    figfile='primary_gain_phase_solutions.png')
        if args.secondary:
            plotcal(caltable=args.gtable,
                    xaxis='time', yaxis='phase',
                    field=args.secondary,
                    plotrange=[-1, -1, -180, 180],
                    showgui=args.verbose,
                    figfile='secondary_gain_phase_solution.png')
        print_msg("Flux density for the flux calibrator, if corrected, "
                  "should lie close to or around 1"
                  "Fluxes for secondary calibrators have not been corrected yet "
                  "and are offset")
        if args.primary:
            plotcal(caltable=args.gtable,
                    xaxis='time', yaxis='amp',
                    field=args.primary,
                    showgui=args.verbose,
                    figfile='primary_gain_amp_solutions.png')
        if args.secondary:
            plotcal(caltable=args.gtable,
                    xaxis='time', yaxis='amp',
                    field=args.secondary,
                    showgui=args.verbose,
                    figfile='secondary_gain_amp_solutions.png')

# -fin-
