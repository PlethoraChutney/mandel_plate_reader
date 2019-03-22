Cimport numpy as np
import pandas as pd
import sys
import os
import argparse
import subprocess
import re

skip_rows = 2
time_regex = re.compile('[0-9]{1,2}:[0-9]{2}')

def get_file_list(directory, quiet = False):
    file_list = []
    for file in os.listdir(directory):
        if file.endswith(".txt"):
            file_list.append(os.path.join(directory, file))

    if not quiet:
        print(f'Found {len(file_list)} files')

    return file_list

def get_seconds(time_str):
    m, s = time_str.split(':')
    return int(m)*60 + int(s)

file = get_file_list('test_data/')[0]
file


def collect_data(file):
    data = pd.read_csv(file, engine = 'python', delimiter = '\t', skiprows = 2, usecols = [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13])
    data

    plate = 0
    sec_per_plate = {0:0, 1:125, 2:425}
    sample_per_plate = {0:'ACMA', 1:'CCCP', 2:'Na_Iono'}
    to_return = pd.DataFrame(columns = ['Time', 'Sample', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9', 'A10', 'A11', 'A12'])

    for row in range(data.shape[0]):
        if str(data.loc[row]['Time(hh:mm:ss)']) == 'Time(hh:mm:ss)':
            plate = plate + 1
        if re.match(time_regex, str(data.loc[row]['Time(hh:mm:ss)'])) is not None:
            Time = get_seconds(str(data.loc[row]['Time(hh:mm:ss)'])) + sec_per_plate[plate]
            Sample = sample_per_plate[plate]
            A1 = data.loc[row]['1']
            A2 = data.loc[row]['2']
            A3 = data.loc[row]['3']
            A4 = data.loc[row]['4']
            A5 = data.loc[row]['5']
            A6 = data.loc[row]['6']
            A7 = data.loc[row]['7']
            A8 = data.loc[row]['8']
            A9 = data.loc[row]['9']
            A10 = data.loc[row]['10']
            A11 = data.loc[row]['11']
            A12 = data.loc[row]['12']
            B1 = data.loc[row + 1]['1']
            B2 = data.loc[row + 1]['2']
            B3 = data.loc[row + 1]['3']
            B4 = data.loc[row + 1]['4']
            B5 = data.loc[row + 1]['5']
            B6 = data.loc[row + 1]['6']
            B7 = data.loc[row + 1]['7']
            B8 = data.loc[row + 1]['8']
            B9 = data.loc[row + 1]['9']
            B10 = data.loc[row + 1]['10']
            B11 = data.loc[row + 1]['11']
            B12 = data.loc[row + 1]['12']
            C1 = data.loc[row + 2]['1']
            C2 = data.loc[row + 2]['2']
            C3 = data.loc[row + 2]['3']
            C4 = data.loc[row + 2]['4']
            C5 = data.loc[row + 2]['5']
            C6 = data.loc[row + 2]['6']
            C7 = data.loc[row + 2]['7']
            C8 = data.loc[row + 2]['8']
            C9 = data.loc[row + 2]['9']
            C10 = data.loc[row + 2]['10']
            C11 = data.loc[row + 2]['11']
            C12 = data.loc[row + 2]['12']
            D1 = data.loc[row + 3]['1']
            D2 = data.loc[row + 3]['2']
            D3 = data.loc[row + 3]['3']
            D4 = data.loc[row + 3]['4']
            D5 = data.loc[row + 3]['5']
            D6 = data.loc[row + 3]['6']
            D7 = data.loc[row + 3]['7']
            D8 = data.loc[row + 3]['8']
            D9 = data.loc[row + 3]['9']
            D10 = data.loc[row + 3]['10']
            D11 = data.loc[row + 3]['11']
            D12 = data.loc[row + 3]['12']
            E1 = data.loc[row + 4]['1']
            E2 = data.loc[row + 4]['2']
            E3 = data.loc[row + 4]['3']
            E4 = data.loc[row + 4]['4']
            E5 = data.loc[row + 4]['5']
            E6 = data.loc[row + 4]['6']
            E7 = data.loc[row + 4]['7']
            E8 = data.loc[row + 4]['8']
            E9 = data.loc[row + 4]['9']
            E10 = data.loc[row + 4]['10']
            E11 = data.loc[row + 4]['11']
            E12 = data.loc[row + 4]['12']
            F1 = data.loc[row + 5]['1']
            F2 = data.loc[row + 5]['2']
            F3 = data.loc[row + 5]['3']
            F4 = data.loc[row + 5]['4']
            F5 = data.loc[row + 5]['5']
            F6 = data.loc[row + 5]['6']
            F7 = data.loc[row + 5]['7']
            F8 = data.loc[row + 5]['8']
            F9 = data.loc[row + 5]['9']
            F10 = data.loc[row + 5]['10']
            F11 = data.loc[row + 5]['11']
            F12 = data.loc[row + 5]['12']
            G1 = data.loc[row + 6]['1']
            G2 = data.loc[row + 6]['2']
            G3 = data.loc[row + 6]['3']
            G4 = data.loc[row + 6]['4']
            G5 = data.loc[row + 6]['5']
            G6 = data.loc[row + 6]['6']
            G7 = data.loc[row + 6]['7']
            G8 = data.loc[row + 6]['8']
            G9 = data.loc[row + 6]['9']
            G10 = data.loc[row + 6]['10']
            G11 = data.loc[row + 6]['11']
            G12 = data.loc[row + 6]['12']
            H1 = data.loc[row + 7]['1']
            H2 = data.loc[row + 7]['2']
            H3 = data.loc[row + 7]['3']
            H4 = data.loc[row + 7]['4']
            H5 = data.loc[row + 7]['5']
            H6 = data.loc[row + 7]['6']
            H7 = data.loc[row + 7]['7']
            H8 = data.loc[row + 7]['8']
            H9 = data.loc[row + 7]['9']
            H10 = data.loc[row + 7]['10']
            H11 = data.loc[row + 7]['11']
            H12 = data.loc[row + 7]['12']
