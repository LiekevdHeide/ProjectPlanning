# -*- coding: utf-8 -*-
"""
Created 25-1
Contains: startup of algorithm.
"""
import numpy as np
import timeit

# own functions
import parserFunc

np.set_printoptions(threshold=np.inf)


def main():
    # get experiment setting
    parserFunc.parse_inputs()

    startTime = timeit.default_timer()

    runTime = timeit.default_timer() - startTime


# execute main() function
if __name__ == "__main__":
    main()
