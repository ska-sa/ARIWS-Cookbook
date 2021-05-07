# Processing MeerKAT data with CASA

0. Find the relevant observation in the SARAO archive to view the calibration report for data quality,
   as well as obtain a `katdal` token for access.

1. Convert the MVF file to a CASA measurement using the `mvftoms.py` script selecting
   cross-correlation visibilities.

2. Start the CASAPy interface and view the measurement set.

3. Apply the standard L-band band edge and RFI flags for MeerKAT using the utility script:
   ```
   run flagging_mkat_lband.py --msfile <filename.ms> --zeros --bp --lband --gps --glonass --galileo
   --iridium --inmarsat`
   ```
   Functionality is illustrated in the notebook
   [L_band_RFI_frequency_flagging.ipynb](https://github.com/rubyvanrooyen/ARIWS-Cookbook/blob/main/casa/L_band_RFI_frequency_flagging.ipynb)

4. Default flagging is followed by data inspection and manual flagging.
   Since the data files are very large, this generally requires some form of averaging or selection
   when using the `plotms` CASA viewer.

   Slice in time (look at all channels averaged over time)
   ```
   plotms(vis=<msfile>, xaxis='channel', yaxis='phase', averagedata=True, avgtime='30000',
   correlation='XX,YY', field=<flux calibrator>, iteraxis='antenna', coloraxis='baseline')

   plotms(vis=<msfile>, xaxis='channel', yaxis='phase', ydatacolumn='data', correlation='XX,YY',
   field=<calibrator>, coloraxis='corr', plotrange=[0,0,-180, 180], averagedata=True, avgtime='30000',
   avgbaseline=True)

   plotms(vis=<msfile>, xaxis='channel', yaxis='phase', averagedata=True, avgbaseline=True,
   correlation='XX,YY', field=<calibrator>, iteraxis='scan', coloraxis='corr')

   plotms(vis=<msfile>, xaxis='channel', yaxis='amp',  correlation='XX,YY', field=<calibrator>,
   iteraxis='antenna', coloraxis='corr', averagedata=True, avgtime='30000')
   ```

   Slice in frequency (look at all timestamps averaged over channel)
   ```
   plotms(vis=<msfile>, xaxis='time', yaxis='phase', correlation='XX,YY', field=<calibrator>, coloraxis='corr',
   averagedata=True, avgbaseline=True)

   plotms(vis=<msfile>, xaxis='time', yaxis='amp', correlation='XX,YY', field=<calibrator>, coloraxis='corr',
   averagedata=True, avgbaseline=True, avgchannel='4096')

   plotms(vis=<msfile>, xaxis='time', yaxis='amp', correlation='XX,YY', field=<calibrator>, coloraxis='corr',
   averagedata=True, avgbaseline=True, avgchannel='4096', iteraxis='scan')
   ```

   Functionality is illustrated in the notebook
   [Inspect_and_flagging_calibrators.ipynb](https://github.com/rubyvanrooyen/ARIWS-Cookbook/blob/main/casa/Inspect_and_flagging_calibrators.ipynb)

5. Standard antenna based calibration
   ```
   run calibrating_mkat_lband.py --msfile <filename.ms> -f <f_cal,...> [-t <target,...>] [-g <g_cal,...>]
   [-b <bp_cal,...>] [-r <ref_ant>]
   ```
   Additionally, some tags may be added to:
   * Correct the phase center, `--fixvis`
   * Apply calibration solutions to calibrators and targets, `--applycal`
   * View CASA command being applied, `--verbose`
   * Only view CASA commands and do not calculate calibration solutions, `--debug`

   Use `run calibrating_mkat_lband.py -h` to view all available options

   Functionality is illustrated in the notebook
   [Calibrating data.ipynb](https://github.com/ska-sa/MeerKAT-Cookbook/blob/master/casa/Calibrating%20data.ipynb)

   View calibration results in calibration tables.
   Note: for gain calibration tables, the targets to plot must be specified by either selecting
   to display the primary calibrators, or the gain ('secondary') calibrator
   ```
   run inspect_cal_solutions.py [--delaycal <ktable>] [--bpcal <btable>] [[--gaincal <gtable>]
   [--primary <b_cal>] [--secondary <g_cal>]]
   ```
   Relevant images will be produced as PNG format in the working directory

   Functionality is illustrated in the notebook
   [Verify calibrated data and calibrate target.ipynb](https://github.com/ska-sa/MeerKAT-Cookbook/blob/master/casa/Verify%20calibrated%20data%20and%20calibrate%20target.ipynb)

   View calibrated data for calibrators to highlight if further flagging is needed
   ```
   plotms(vis=<msfile>, xaxis='channel', yaxis='phase', ydatacolumn='corrected', averagedata=True,
   avgtime='30000', correlation='XX,YY', field=<flux calibrator>, iteraxis='antenna',
   coloraxis='baseline')


   plotms(vis=<msfile>, xaxis='channel', yaxis='phase', ydatacolumn='corrected', averagedata=True,
   avgtime='30000', avgbaseline=True, avgchannel='64', correlation='XX,YY', field=<calibrators>,
   coloraxis='field')


   plotms(vis=<msfile>, xaxis='channel', yaxis='amp', ydatacolumn='corrected', averagedata=True,
   avgtime='30000', avgbaseline=True, avgchannel='64', correlation='XX,YY', field=<calibrators>,
   coloraxis='field')


   plotms(vis=<msfile>, xaxis='time', yaxis='amp', ydatacolumn='corrected', averagedata=True,
   avgbaseline=True, avgchannel='4096', correlation='XX,YY', field=<calibrator(s)>, coloraxis=<'field'
   or 'corr'>)
   ```

   Validation of calibration solutions
   ```
   plotms(vis=<msfile>, xaxis='imag', yaxis='real', correlation='XX,YY', xdatacolumn='corrected',
   ydatacolumn='corrected', field=<calibrator>, avgscan=False, coloraxis='scan', spw='*:2100~2300')

   plotms(vis=<msfile>, xaxis='phase', yaxis='amp', correlation='XX,YY', xdatacolumn='corrected',
   ydatacolumn='corrected', field=<calibrator>, avgscan=False, coloraxis='corr', spw='*:2100~2300')
   ```

   View calibrated targets and flag before imaging
   ```
   plotms(vis=<msfile>, xaxis='time', yaxis='amp', ydatacolumn='corrected', correlation='XX,YY',
   field=<target>, coloraxis='corr', averagedata=True, avgbaseline=True, avgchannel='4096')
   ```

6. Imaging is more efficient using `wsclean`, some CASA examples are presented in two notebooks    
   [Calibrator imaging.ipynb](https://github.com/ska-sa/MeerKAT-Cookbook/blob/master/casa/Calibrator%20imaging.ipynb)    
   [Imaging spectral line.ipynb](https://github.com/ska-sa/MeerKAT-Cookbook/blob/master/casa/Imaging%20spectral%20line.ipynb)


**Summary**    
The notebooks and CASA script provide an introduction to interacting with MeerKAT data.
Processing of very large files are best done using pipelines such as [MeerKATHI](https://pypi.org/project/meerkathi/).
The notebook recipes closely follow an example configuration input file (`config.yml`) for MeerKATHI pipeline implementation.

-fin-
