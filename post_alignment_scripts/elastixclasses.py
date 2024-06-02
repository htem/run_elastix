#!/usr/bin/env python3

import os


class ElastixLog():
    def __init__(self, filename='.'):
        if os.path.isdir(filename):
            filename = os.path.join(filename, 'elastix.log')
        self.filename = filename
        with open(filename, 'r') as f:
            self.text = f.read().splitlines()

    def find_line(self,
                  first_or_last='first',
                  startswith=None,
                  endswith=None):
        if first_or_last == 'first':
            indices = range(len(self.text))
        elif first_or_last == 'last':
            indices = range(len(self.text)-1, -1, -1)
        else:
            raise ValueError('first_or_last must be "first" or "last"')

        for n in indices:
            line = self.text[n]
            if startswith is None or line.startswith(startswith):
                if endswith is None or line.endswith(endswith):
                    return n
        raise ValueError('Line not found')

    @property
    def final_metric_value(self):
        n = self.find_line('last',
                           startswith='Final metric value')
        return float(self.text[n].split('=')[1].strip())

    @property
    def final_bending_metric(self):
        n = self.find_line('last',
                           startswith='Time spent in resolution')
        return float(self.text[n-1].split('\t')[3])

    @property
    def final_correlation(self):
        n = self.find_line('last',
                           startswith='Time spent in resolution')
        return float(self.text[n-1].split('\t')[2])

    def good_results(self,
                     correlation_threshold=-0.96,
                     bending_threshold=0.0000035,
                     verbose=True):
        message = ''
        if (correlation_threshold is not None
                and self.final_correlation > correlation_threshold):
            message += 'Correlation is bad. '
        if (bending_threshold is not None
                and self.final_bending_metric > bending_threshold):
            message += 'Bending is severe. '
        if message != '':
            if verbose:
                print(message)
            return False
        return True

    def asgd_settings(self, resolution='all', entries=6):
        if resolution == 'all':
            prefix = 'Settings of AdaptiveStochasticGradientDescent for all resolutions'
        elif isinstance(resolution, int):
            prefix = f'Settings of AdaptiveStochasticGradientDescent in resolution {resolution}'
        n = self.find_line('first', startswith=prefix)
        settings = dict()
        for i in range(entries):
            words = self.text[n+i+1][2:-2].split(' ')
            settings[words[0]] = [float(s) for s in words[1:]]

        return settings
