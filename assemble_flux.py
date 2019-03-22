import numpy as np
import pandas as pd
import sys
import os
import argparse
import subprocess
import re

skip_rows = 2
time_regex = re.compile('[0-9]{1,2}:[0-9]{2}')
script_path = dir_path = os.path.dirname(os.path.realpath(__file__))

def get_file_list(directory, quiet = False):
    file_list = []
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            file_list.append(os.path.join(directory, file))

    if not quiet:
        print(f'Found {len(file_list)} files')

    return file_list

def collect_data(file, time_increment, quiet):
    if not quiet:
        print(f'Reading plate file {file}')

    data = pd.read_csv(file, engine = 'python', delimiter = '\t', skiprows = 2, usecols = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])

    plate = 0
    time_index = 0
    sample_per_plate = {0:'ACMA', 1:'CCCP', 2:'Na_Iono'}

    if not quiet:
        print('Assembling plate reads')

    rows_list = []
    for row in range(data.shape[0]):
        # the plate reader writes the time only once each time it reads the plate
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
    parser.add_argument('-d', '--directory', default = script_path, help = 'What directory is your file in. Default is same as this script.')
    parser.add_argument('-o', '--outfile', default = os.path.join(script_path, 'assembled_flux.csv'), help = 'Full path to saved csv. Default \'assembled_flux.csv\' in script dir')
    parser.add_argument('-i', '--interval', default = 5, type = int, help = 'Time interval between reads in seconds. Default 5')
    parser.add_argument('-q', '--quiet', default = False, action = 'store_true', help = 'Squelch messages. Default False')

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(0)
    args = parser.parse_args()

    dir = os.path.normpath(args.directory)
    outfile = os.path.normpath(args.outfile)
    outdir = os.path.dirname(outfile)
    time_increment = args.interval
    quiet = args.quiet

    if os.path.isfile(outfile):
        print(f'I don\'t want to overwrite the file {outfile}. Please move or delete it first.')
        sys.exit()

    file_list = get_file_list(dir, quiet)
    plate_data = collect_data(file_list[0], time_increment, quiet)

    if not quiet:
        print('Saving csv')

    plate_data.to_csv(outfile, index = False)

    if not quiet:
        print('Making plots')
    subprocess.run(['Rscript', '--quiet', os.path.join(script_path, 'make_plot.R'), outfile])
    if os.path.isfile(os.path.join(outdir, 'Rplots.pdf')) :
        os.remove(os.path.join(outdir, 'Rplots.pdf'))
    if not quiet:
        print('Done.')
