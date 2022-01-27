'''Classes and methods to denoise Sentinel1 images'''

import numpy as np

from s1denoise import Sentinel1Image


class S1Image(Sentinel1Image):
    
    def __init__(self, filename, mapper_name='sentinel1_l1', log_level=30):
        super().__init__(str(filename), mapperName=mapper_name, logLevel=log_level)
        self.sigma0 = np.array([])
        self.nesz = np.array([])
        self.nesz_scaled = np.array([])
        self.sigma0_denoised = np.array([])


    def calculate_scaling_factors(self):
        pass
