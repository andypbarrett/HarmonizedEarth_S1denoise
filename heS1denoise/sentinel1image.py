'''Classes and methods to denoise Sentinel1 images'''

from s1denoise import Sentinel1Image


class S1Image(Sentinel1Image):
    
    def __init__(self, filename, mapper_name='sentinel1_l1', log_level=30):
        super().__init__(str(filename), mapperName=mapper_name, logLevel=log_level)
        self.sigma0 = []
        self.nesz = []
        self.nesz_scaled = []
        self.sigma0_denoised = []


    def calculate_scaling_factors(self):
        pass
