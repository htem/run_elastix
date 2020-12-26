#!/usr/bin/env python3

# Wrapper for the program transformix, part of the library elastix https://elastix.lumc.nl/

# Other versions of this script with example applications can be found at 
# https://github.com/htem/GridTape_VNC_paper/blob/main/template_registration_pipeline/register_EM_dataset_to_template/warp_points_between_FANC_and_template.py
# and
# https://github.com/htem/pymaid_addons/blob/main/pymaid_addons/coordinate_transforms/warp_points_between_FANC_and_template.py

import os
import os.path
import subprocess
import numpy as np


def transformix(points, transformation_file):
    """
    Take an Nx3 numpy array representing N different x, y, z coordinate
    triplets and return an Nx3 numpy array representing the transformed
    coordinates, using the program transformix and the specified
    transformation_file.
    """
    def write_points_as_transformix_input_file(points, fn):
        with open(fn, 'w') as f:
            f.write('point\n{}\n'.format(len(points)))
            for x, y, z in points:
                f.write('%f %f %f\n'%(x, y, z))

    starting_dir = os.getcwd()
    if '/' in transformation_file:
        os.chdir(os.path.dirname(transformation_file))

    for fn in ['transformix_input.txt', 'outputpoints.txt', 'transformix.log']:
        if os.path.exists(fn):
            m = ('Temporary file '+fn+' already exists in '+os.getcwd()+'. '
                 'Continuing will delete it. Continue? [Y/n] ')
            if input(m).lower() != 'y':
                wd = os.getcwd()
                os.chdir(starting_dir)
                raise FileExistsError(wd+'/'+fn+' must be removed.')
            else:
                os.remove(fn)

    try:
        fn = 'transformix_input.txt'
        write_points_as_transformix_input_file(points, fn)
        transformix_cmd = 'transformix -out ./ -tp {} -def {}'.format(
            transformation_file,
            fn
        )
        try:
            m = subprocess.run(transformix_cmd.split(' '),
                               stdout=subprocess.PIPE)
        except FileNotFoundError as e:
            if "No such file or directory: 'transformix'" in e.strerror:
                raise FileNotFoundError(
                    'transformix executable not found on shell PATH.'
                    ' Is elastix installed? Is it on your PATH?')
            else:
                raise
        if not os.path.exists('outputpoints.txt'):
            print(m.stdout.decode())
            raise Exception('transformix failed, see output above for details.')

        new_pts = []
        with open('outputpoints.txt', 'r') as transformix_out:
            for line in transformix_out.readlines():
                output = line.split('OutputPoint = [ ')[1].split(' ]')[0]
                new_pts.append([float(i) for i in output.split(' ')])
    finally:
        try: os.remove('transformix_input.txt')
        except: pass
        try: os.remove('outputpoints.txt')
        except: pass
        try: os.remove('transformix.log')
        except: pass
        os.chdir(starting_dir)

    return np.array(new_pts)
