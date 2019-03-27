#!/usr/bin/env python3
import numpy as np
import pandas as pd
import sys
import os
import argparse
import subprocess
import re

skip_rows = 2
time_regex = re.compile('[0-9]{1,2}:[0-9]{2}')
script_path = os.path.dirname(os.path.realpath(__file__))

def get_file_list(directory, quiet = False):
    file_list = []
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            file_list.append(os.path.join(directory, file))

    if not quiet:
        print(f'Found {len(file_list)} files')

    return file_list

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
        #
        # We'll look for a header to indicate that the next plate has started,
        # and we'll (painstakingly) get the fluorescence for each well by finding
        # a time expression and moving around from there.
        #
        # This whole process is the slow part of the script, even using the list-
        # of-dictionaries method, which is apparently the fastest.
        if str(data.loc[row]['Time(hh:mm:ss)']) == 'Time(hh:mm:ss)':
            plate = plate + 1
        if re.match(time_regex, str(data.loc[row]['Time(hh:mm:ss)'])) is not None:
            single_row = {}
            single_row.update(
                Sample = sample_per_plate[plate],
                A01  = data.loc[row]['1'],
                A02  = data.loc[row]['2'],
                A03  = data.loc[row]['3'],
                A04  = data.loc[row]['4'],
                A05  = data.loc[row]['5'],
                A06  = data.loc[row]['6'],
                A07  = data.loc[row]['7'],
                A08  = data.loc[row]['8'],
                A09  = data.loc[row]['9'],
                A10 = data.loc[row]['10'],
                A11 = data.loc[row]['11'],
                A12 = data.loc[row]['12'],
                B01  = data.loc[row + 1]['1'],
                B02  = data.loc[row + 1]['2'],
                B03  = data.loc[row + 1]['3'],
                B04  = data.loc[row + 1]['4'],
                B05  = data.loc[row + 1]['5'],
                B06  = data.loc[row + 1]['6'],
                B07  = data.loc[row + 1]['7'],
                B08  = data.loc[row + 1]['8'],
                B09  = data.loc[row + 1]['9'],
                B10 = data.loc[row + 1]['10'],
                B11 = data.loc[row + 1]['11'],
                B12 = data.loc[row + 1]['12'],
                C01  = data.loc[row + 2]['1'],
                C02  = data.loc[row + 2]['2'],
                C03  = data.loc[row + 2]['3'],
                C04  = data.loc[row + 2]['4'],
                C05  = data.loc[row + 2]['5'],
                C06  = data.loc[row + 2]['6'],
                C07  = data.loc[row + 2]['7'],
                C08  = data.loc[row + 2]['8'],
                C09  = data.loc[row + 2]['9'],
                C10 = data.loc[row + 2]['10'],
                C11 = data.loc[row + 2]['11'],
                C12 = data.loc[row + 2]['12'],
                D01  = data.loc[row + 3]['1'],
                D02  = data.loc[row + 3]['2'],
                D03  = data.loc[row + 3]['3'],
                D04  = data.loc[row + 3]['4'],
                D05  = data.loc[row + 3]['5'],
                D06  = data.loc[row + 3]['6'],
                D07  = data.loc[row + 3]['7'],
                D08  = data.loc[row + 3]['8'],
                D09  = data.loc[row + 3]['9'],
                D10 = data.loc[row + 3]['10'],
                D11 = data.loc[row + 3]['11'],
                D12 = data.loc[row + 3]['12'],
                E01  = data.loc[row + 4]['1'],
                E02  = data.loc[row + 4]['2'],
                E03  = data.loc[row + 4]['3'],
                E04  = data.loc[row + 4]['4'],
                E05  = data.loc[row + 4]['5'],
                E06  = data.loc[row + 4]['6'],
                E07  = data.loc[row + 4]['7'],
                E08  = data.loc[row + 4]['8'],
                E09  = data.loc[row + 4]['9'],
                E10 = data.loc[row + 4]['10'],
                E11 = data.loc[row + 4]['11'],
                E12 = data.loc[row + 4]['12'],
                F01  = data.loc[row + 5]['1'],
                F02  = data.loc[row + 5]['2'],
                F03  = data.loc[row + 5]['3'],
                F04  = data.loc[row + 5]['4'],
                F05  = data.loc[row + 5]['5'],
                F06  = data.loc[row + 5]['6'],
                F07  = data.loc[row + 5]['7'],
                F08  = data.loc[row + 5]['8'],
                F09  = data.loc[row + 5]['9'],
                F10 = data.loc[row + 5]['10'],
                F11 = data.loc[row + 5]['11'],
                F12 = data.loc[row + 5]['12'],
                G01  = data.loc[row + 6]['1'],
                G02  = data.loc[row + 6]['2'],
                G03  = data.loc[row + 6]['3'],
                G04  = data.loc[row + 6]['4'],
                G05  = data.loc[row + 6]['5'],
                G06  = data.loc[row + 6]['6'],
                G07  = data.loc[row + 6]['7'],
                G08  = data.loc[row + 6]['8'],
                G09  = data.loc[row + 6]['9'],
                G10 = data.loc[row + 6]['10'],
                G11 = data.loc[row + 6]['11'],
                G12 = data.loc[row + 6]['12'],
                H01  = data.loc[row + 7]['1'],
                H02  = data.loc[row + 7]['2'],
                H03  = data.loc[row + 7]['3'],
                H04  = data.loc[row + 7]['4'],
                H05  = data.loc[row + 7]['5'],
                H06  = data.loc[row + 7]['6'],
                H07  = data.loc[row + 7]['7'],
                H08  = data.loc[row + 7]['8'],
                H09  = data.loc[row + 7]['9'],
                H10 = data.loc[row + 7]['10'],
                H11 = data.loc[row + 7]['11'],
                H12 = data.loc[row + 7]['12'],
            )
            rows_list.append(single_row)

    to_return = pd.DataFrame(rows_list)
    # Since the plate reader prints a read even for times that it didn't read the
    # plate (!), we need a way to only keep records we have and correctly track
    # the total time.
    #
    # Here we drop rows where all cells are NA (i.e., plates that weren't read;
    # we also ignore the column with the Sample in it, since that's
    # filled in by the script in all rows), then multiply the row number by the time
    #interval (provided by the user in arguments) to get the total time.
    to_return.dropna(inplace = True, how = 'all', subset = to_return.columns[0:95])
    to_return.reset_index(inplace = True, drop = True)
    to_return['Time (s)'] = to_return.index * time_increment

    if not quiet:
        print('Done reading file')

    return to_return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'A script to assemble kinetic fluorescence readings from an old plate reader')
    renamers = parser.add_mutually_exclusive_group()
    parser.add_argument('directory', help = 'What directory is your file in.')
    parser.add_argument('-o', '--outfile', default = None, help = 'Full path to saved csv. Default \'plates.csv\' in target dir')
    parser.add_argument('-i', '--interval', default = 5, type = int, help = 'Time interval between reads in seconds. Default 5')
    parser.add_argument('-p', '--plates', nargs = '+', default = ['ACMA', 'CCCP', 'Na_Iono'], help = 'List of reagents used separated by spaces. Default is for Na flux')
    renamers.add_argument('-s', '--samples', nargs = '+', help = 'List of wells and samples, separated by spaces. Samples with the same name are averaged. _ becomes -')
    renamers.add_argument('-r', '--rangerename', nargs = '+', help = 'Rename several wells at once. Give upper left and lower right well, then samples names (left to right, top to bottom)')
    parser.add_argument('-q', '--quiet', default = False, action = 'store_true', help = 'Squelch messages. Default False')

    args = parser.parse_args()
    outfile = args.outfile
    dir = os.path.normpath(args.directory)
    time_increment = args.interval
    quiet = args.quiet
    plates = args.plates
    samples = args.samples
    range_rename = args.rangerename

    # Get directories and filenames in order
    if outfile is None:
        outfile = os.path.join(os.path.dirname(args.directory), 'plates.csv')
    else:
        outfile = os.path.normpath(args.outfile)
    outdir = os.path.dirname(outfile)

    if os.path.isfile(outfile):
        if not quiet:
            print(f'I don\'t want to overwrite the file {os.path.abspath(outfile)}. Please move or delete it first.')
        sys.exit(1)

    # Figure out what plates we're using
    sample_per_plate = generate_plates(plates)

    # Get files and save plots and data
    file_list = get_file_list(dir, quiet)
    plate_data = collect_data(file_list[0], time_increment, quiet)

    if samples is not None:
        rename_wells(samples, plate_data)

    if range_rename is not None:
        wells_by_range(range_rename[0:2], range_rename[2:len(range_rename)+1], plate_data, quiet)

    if not quiet:
        print('Saving csv')

    plate_data.to_csv(outfile, index = False)

    if not quiet:
        print('Making plots')
    subprocess.run(['Rscript', '--quiet', os.path.join(script_path, 'make_plot.R'), outfile], stderr = open(os.devnull, 'wb'))
    if os.path.isfile(os.path.join(script_path, 'Rplots.pdf')) :
        os.remove(os.path.join(script_path, 'Rplots.pdf'))
    if not quiet:
        print('Done.')
