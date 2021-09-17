#!/usr/bin/env python3

# Wrapper for the program transformix, part of the library elastix https://elastix.lumc.nl/

# Other versions of this script with example applications can be found at 
# https://github.com/htem/GridTape_VNC_paper/blob/main/template_registration_pipeline/register_EM_dataset_to_template/warp_points_between_FANC_and_template.py
# and
# https://github.com/htem/pymaid_addons/blob/main/pymaid_addons/coordinate_transforms/warp_points_between_FANC_and_template.py

import sys
import os
import os.path
import subprocess

import numpy as np

import transformix  # See https://github.com/jasper-tms/pytransformix


def show_help():
    print('Usage: transform_swc.py swc_file transform_file')
    print('Takes the swc_file and applies the transformation specified by transform_file using elastix\'s function transformix.')

    #print('This function is mainly intended for transforming neuron tracings from light or electron microscopy into the VNC atlas coordinate system.')
    #print('Set swc_side to be the side of the VNC the neuron was originally on. Then the output files will be correctly named with _left or _right')
    #print('to indicate the position of the output neurons within the VNC atlas.')
    #print('Set generate_flipped_swc to True to generate both the _left and _right outputs.')
    # [swc_side=left] [generate_flipped_swc=True]')

# TODO this
#def transform_swc_to_VNC_template(swc_file, transformation_file, swc_side='left', generate_flipped_swc=True):
#    """
#    something something call transform_swc and then call it again if the user
#    wants a flipped one
#    """
#
#    raise NotImplementedError
#
#    assert swc_side in ['left', 'right']
#
#    if swc_side == 'left':
#        filename_modifier = '_inTemplateSpace_left.swc'
#    else:
#        filename_modifier = '_inTemplateSpace_right.swc'
#    with open(os.path.join(output_dir,swc_file.replace('.swc', filename_modifier)), 'w') as fout:
#        for a,b,c,d,e,f,g in swc_data:
#            fout.write("%d %d %f %f %f %d %d\n"%(a,b,c,d,e,f,g))
#
#    if generate_flipped_swc:
#        swc_data[:, 2] = 263200-swc_data[:, 2] #Left-right flip across the template's midline.
#        if swc_side == 'left':
#            filename_modifier = '_inTemplateSpace_right.swc'
#        else:
#            filename_modifier = '_inTemplateSpace_left.swc'
#        with open(os.path.join(output_dir,swc_file.replace('.swc', filename_modifier)), 'w') as fout:
#            for a,b,c,d,e,f,g in swc_data:
#                fout.write("%d %d %f %f %f %d %d\n"%(a,b,c,d,e,f,g))
#    pass

def transform_swc(swc_filename, transformation_file):
    """
    Transform the coordinates in an .swc file (typically representing points of
    a skeleton model of a neuron) according to the transformation parameters
    specified in the transformation_file
    """
    #TODO add some of the features from warp_points_between_FANC_and_template.py
    #like input_units and output_units maybe?
    assert isinstance(swc_filename, str) and swc_filename.endswith('.swc')

    # Load
    swc_data, swc_comments = load_swc(swc_filename, return_comments=True)

    # Transform
    swc_data[:, 2:5] = transformix.transform_points(swc_data[:, 2:5], transformation_file)

    # Save
    save_swc(swc_data,
             swc_filename.replace('.swc', '_transformed.swc'),
             comments=swc_comments)


# --- some swc utillities --- #
def load_swc(swc_filename, return_comments=True):
    """
    Open an swc file and return its data as an Nx7 numpy array, and optionally
    return any text comments at the start of the file.
    """
    array = np.genfromtxt(swc_filename)
    if return_comments:
        with open(swc_filename, 'r') as f:
            comments = ''.join([l for l in f.readlines() if l[0] == '#'])
        return array, comments
    else:
        return array


def save_swc(array, filename, comments=None, decimals=6, delimiter='\t'):
    """
    Save an Nx7 array of numbers to file in .swc format.

    comments (str): This string, if provided, will be saved as the first
        line(s) of the .swc file. The provided string must already be formatted
        with lines starting with '#' characters and newlines where desired.

    decimals (int): how many decimals to write to file for columns 3-6 of the
        swc file (the columns representing x, y, z, and radius). The other
        columns are integer values so are not affected by this parameter.

    delimeter (str): character to separate columns of the swc file. '\\t' or ' '
        are standard.
    """
    if not _ok_to_write_to(filename):
        return

    if array.shape == (7,):
        save(np.array([array]), filename, comments, decimals, delimiter)
    if len(array.shape) != 2 or array.shape[1] != 7:
        raise ValueError('Nx7 array required but got an array with shape '
                         '{}'.format(array.shape))

    int_pattern = '{:.0f}'
    if decimals is None:
        float_pattern = '{}'
    else:
        float_pattern = '{:.' + str(int(decimals)) + 'f}'
    pattern = '{i}{d}{i}{d}{f}{d}{f}{d}{f}{d}{f}{d}{i}\n'.format(
        i=int_pattern,
        f=float_pattern,
        d=delimiter)

    with open(filename, 'w') as output_file:
        output_file.write(comments)
        for row in array:
            output_file.write(pattern.format(*row))


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        show_help()
    else:
        try:
            transform_swc(sys.argv[1], sys.argv[2])
        except:
            show_help()
            raise
