# coding=utf-8

import numpy
import matplotlib.style
from six.moves import range
from matplotlib import pyplot
matplotlib.style.use('ggplot')


class StatisticalInformation(object):
    def __init__(self):
        self._data = {}

    def add_datapoint(self, key, value):
        self._data.setdefault(key, []).append(value)

    @staticmethod
    def _get_optimum_bins(plotdata_y):
        """
        Histogram Binwidth Optimization Method

        ::

            Shimazaki and Shinomoto, Neural Comput 19 1503-1527, 2007
            2006 Author Hideaki Shimazaki, Matlab
            Department of Physics, Kyoto University
            shimazaki at ton.scphys.kyoto-u.ac.jp

        This implementation based on the version in python
        written by Érbet Almeida Costa

        :param plotdata_y: The data for which a histogram is to be made
        :return: The optimal number of bins

        .. warning:: This function fails if the provided data lacks a proper
                     distribution, such as if there are only 4 distinct values
                     in the output. Figure out why and how to fix it. In the
                     meanwhile, specify bins manually to not let this function
                     be called.
        """

        max_p = max(plotdata_y)
        min_p = min(plotdata_y)

        distinct_vals = set(plotdata_y)
        if len(distinct_vals) < 5:
            return len(distinct_vals)

        n_min = 2
        n_max = 25
        n = range(n_min, n_max)

        # Number of Bins array
        n = numpy.array(n)
        # Bin Size Vector
        d = (max_p - min_p) / n

        c = numpy.zeros(shape=(numpy.size(d), 1))

        # Computation of the cost function
        for i in range(numpy.size(n)):
            edges = numpy.linspace(min_p, max_p, n[i] + 1)  # Bin edges
            ki = pyplot.hist(plotdata_y, edges)  # Count # of events in bins
            ki = ki[0]
            k = numpy.mean(ki)  # Mean of event count
            v = sum((ki - k) ** 2) / n[i]  # Variance of event count
            c[i] = (2 * k - v) / ((d[i]) ** 2)  # The cost Function

        # Optimal Bin Size Selection
        cmin = min(c)
        idx = numpy.where(c == cmin)
        idx = int(idx[0])
        pyplot.close()
        return n[idx]

    def histogram(self, key):
        data = self._data.get(key, None)
        if not data:
            return
        pyplot.hist(data, bins=self._get_optimum_bins(data),
                    range=(min(data), max(data)), edgecolor='black')
        pyplot.show()

    def print_table(self, key):
        data = self._data.get(key, None)
        if not data:
            return
        print(data)
