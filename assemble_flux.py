#!/usr/bin/env python3
import numpy as np
import pandas as pd
import sys
import os
import argparse
import subprocess
import re
import string
import shutil

# 1 Hardcoding ----------------------------------------------------------------

skip_rows = 2
time_regex = re.compile('[0-9]{1,2}:[0-9]{2}')
script_path = os.path.dirname(os.path.realpath(__file__))

# 2 Helper functions ----------------------------------------------------------

def generate_plates(plate_list):

    plate_dict = {}
    i = 0
    for plate in plate_list:
        plate_dict[i] = plate
        i += 1
    return plate_dict

def rename_wells(well_list, df):

    rename_map = {}
    i = 0
    while i < len(well_list):
        rename_map[well_list[i].upper()] = well_list[i+1].replace('_', '-')
        i += 2
    df.rename(columns = rename_map, inplace = True)

def wells_by_range(well_limits, samples, df, quiet):
    row_limits = [well_limits[0][0].upper(), well_limits[1][0].upper()]
    column_limits = [int(well_limits[0][1:3]), int(well_limits[1][1:3])]
    expected_num_samples = ((ord(row_limits[1]) - ord(row_limits[0]) + 1) * (column_limits[1] - column_limits[0] + 1))
    if (expected_num_samples != len(samples)):
        if not quiet:
            print(f'Warning: expected {expected_num_samples} sample names and got {len(samples)}. Not renaming.')
        return None

    rows_list = [chr(x) for x in range(ord(row_limits[0]), ord(row_limits[1]) + 1)]
    cols_ints = range(int(column_limits[0]), int(column_limits[1]) + 1)
    cols_list = []
    for col in cols_ints:
        if col < 10:
            cols_list.append('0' + str(col))
        else:
            cols_list.append(str(col))

    sample_indexer = 0
    rename_map = {}
    for row in rows_list:
        for col in cols_list:
            well = row + col
            sample = samples[sample_indexer]
            rename_map[well] = sample.replace('_', '-')
            sample_indexer += 1

    df.rename(columns = rename_map, inplace = True)
    if not quiet:
        print(f'Renaming columns: {rename_map}')

def collect_data(file, time_increment, quiet):
    if not quiet:
        print(f'Reading plate file {file}')

    data = pd.read_csv(file, engine = 'python', delimiter = '\t', skiprows = 2, usecols = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

    plate = 0
    time_index = 0

    if not quiet:
        print('Assembling plate reads')

    rows_list = []
    for row in range(data.shape[0]):
        # The plate reader writes the time only once each time it reads the plate
        # it also writes a new header column each time we switch to a new plate,
        # which we do after adding a reagent

        if str(data.loc[row]['Time(hh:mm:ss)']) == 'Time(hh:mm:ss)':
            plate = plate + 1
        if re.match(time_regex, str(data.loc[row]['Time(hh:mm:ss)'])) is not None:
            single_row = {}

            single_row['Sample'] = sample_per_plate[plate]
            for letter in string.ascii_uppercase[0:8]:
                column_offset = ord(letter) - 65 # ord('A') is 65
                for well in range(1,13):
                    single_row[''.join([letter, f'{well:02}'])] = data.loc[row + column_offset][str(well)]

            rows_list.append(single_row)

    to_return = pd.DataFrame(rows_list)
    # Since the plate reader prints a read even for times that it didn't read the
    # plate (!), we need a way to only keep records we have and correctly track
    # the total time.
    #
    # Here we drop rows where all cells are NA (i.e., plates that weren't read;
    # we also ignore the column with the Sample in it, since that's
    # filled in by the script in all rows), then multiply the row number by the time
    # interval (provided by the user in arguments) to get the total time.
    to_return.dropna(inplace = True, how = 'all', subset = to_return.columns[0:95])
    to_return.reset_index(inplace = True, drop = True)
    to_return['Time (s)'] = to_return.index * time_increment

    if not quiet:
        print('Done reading file')

    return to_return

# 3 Main ----------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'A script to assemble kinetic fluorescence readings from an old plate reader')
    renamers = parser.add_mutually_exclusive_group()
    parser.add_argument('file', help = 'Path to your plate read .txt file')
    parser.add_argument('-o', '--outfile', default = None, help = 'Full path to saved csv. Default \'plates.csv\' in target dir')
    parser.add_argument('-i', '--interval', default = 5, type = int, help = 'Time interval between reads in seconds. Default 5')
    parser.add_argument('-p', '--plates', nargs = '+', default = ['ACMA', 'CCCP', 'Na_Iono'], help = 'List of reagents used separated by spaces. Default is for Na flux')
    renamers.add_argument('-s', '--samples', nargs = '+', help = 'List of wells and samples, separated by spaces. Samples with the same name are averaged. _ becomes -')
    renamers.add_argument('-r', '--rangerename', nargs = '+', help = 'Rename several wells at once. Give upper left and lower right well, then samples names (left to right, top to bottom)')
    parser.add_argument('--deletecol', nargs = '+', help = 'Ignore a column or columns')
    parser.add_argument('-q', '--quiet', default = False, action = 'store_true', help = 'Squelch messages. Default False')
    parser.add_argument('--no-plots', default = False, action = 'store_true', help = 'Don\'t make R plots.')
    parser.add_argument('--copy-manual', default = False, action = 'store_true', help = 'Copy R file for manual plot edits')

    args = parser.parse_args()
    outfile = args.outfile
    file = os.path.normpath(args.file)
    dir = os.path.dirname(file)
    time_increment = args.interval
    quiet = args.quiet
    plates = args.plates
    samples = args.samples
    range_rename = args.rangerename
    to_delete = args.deletecol
    no_plots = args.no_plots
    copy_man = args.copy_manual

    # Get directories and filenames in order
    if outfile is None:
        outfile = os.path.join(dir, 'plates.csv')
    else:
        outfile = os.path.normpath(args.outfile)
    outdir = os.path.dirname(outfile)

    if os.path.isfile(outfile):
        if input(f'Are you sure you want to overwrite the file {os.path.abspath(outfile)}?\n[Y]es / [N]o\n').upper() != 'Y':
            sys.exit(0)

    # Figure out what plates we're using
    sample_per_plate = generate_plates(plates)

    # Get files and save plots and data
    plate_data = collect_data(file, time_increment, quiet)

    if to_delete is not None:
        plate_data.drop(to_delete, axis = 1, inplace = True)

    if samples is not None:
        rename_wells(samples, plate_data)

    if range_rename is not None:
        wells_by_range(range_rename[0:2], range_rename[2:len(range_rename)+1], plate_data, quiet)

    if not quiet:
        print('Saving csv')

    plate_data.to_csv(outfile, index = False)

    if not no_plots:
        if not quiet:
            print('Making plots')
        subprocess.run(['Rscript', '--quiet', os.path.join(script_path, 'make_plot.R'), outfile])
        if os.path.isfile(os.path.join(script_path, 'Rplots.pdf')) :
            os.remove(os.path.join(script_path, 'Rplots.pdf'))
    if copy_manual:
            shutil.copyfile(os.path.join(script_path, 'manual_plot.R'), os.path.join(outdir, 'manual_plot.R'))

    if not quiet:
        print('Done.')
