'''Classes and methods to denoise Sentinel1 images'''

import warnings

import numpy as np

from s1denoise import Sentinel1Image
from s1denoise.utils import fit_noise_scaling_coeff


class S1Image(Sentinel1Image):
    
    def __init__(self, filename, mapper_name='sentinel1_l1', log_level=30):
        super().__init__(str(filename), mapperName=mapper_name, logLevel=log_level)
        self.sigma0 = np.array([])
        self.nesz = np.array([])
        self.nesz_scaled = np.array([])
        self.sigma0_denoised = np.array([])

        self.swath_bounds = {
            'HH': self.import_swathBounds('HH'),
            'HV': self.import_swathBounds('HV'),
            }


    def calculate_scaling_factors(self):
        '''Calculates NESZ noise scaling factors following Sun et al, 2021'''
        block_scaling_factors = {}
        block_scaling_factors['IPFversion'] = s1.IPFversion

        for swid in s1.swath_ids:
            swath_name = f'{s1.obsMode}{swid}'
            block_scaling_factors[swath_name] = NoiseScalingFactorResults()


class NoiseScalingFactorResults:
    '''Class to hold results of scaling factor calculation'''
    def __init__(self):
        self.sigma0 = np.array([])
        self.noise_equivalent_sigma0 = np.array([])
        self.scaling_factor = np.array([])
        self.correlation_coeficient = np.array([])
        self.fit_residual = np.array([])
        self.block_variance = np.array([])


    def get_swath_scaling_factor(self, variance_threshold=10**-7.1):
        '''Calculates the scaling factor for each subswath.  Subswath scaling factors
    are estimated by taking the mean of all scaling_factors for a subswath that have a 
    variance less than variance_threshold.  If no scaling_factors have an associated variance less
    than variance_threshold, the mean of all scaling_factors is used.  Subswath blocks with
    small variance are assumed to be homogeneous and indicative of open water.
    
    :result: dict containing results of scaling factor fit
    :variance_threshold: threshold to include scaling_factors in calculation.  Sun et al (2021)
                         estimated a threshold of 10**-7.1 from 100 images.
                         
    :returns: appends swath_scaling_factor to results dict
    '''
        small_variance = self.block_variance < variance_threshold
        if not any(small_variance):
            swath_scaling_factor = np.nanmean(self.scaling_factor)
        else:
            swath_scaling_factor = np.nanmean(self.scaling_factor[small_variance])
        return swath_scaling_factor


def block_scaling_factor(sigma0, nesz, swath_bounds, *,
                         zoom_step=1, crop=400,
                         azimuth_window=200, minimum_lines=50):
    '''Calculate scaling factor for a block

    :sigma0: raw level-1 sigma0
    :nesz: full noise equivalent sigma zero

    
    :zoom_step: step to sub-sample in range direction
    :crop: buffer for sub-swaths that is ignored in calculating scaling factor

    :returns: NoiseScalingFactorResults instance containing scaling factors and
              associated parameters for each lines
    '''
    pass


def range_profile_average(arr, minimum_lines=None):
    '''Wrapper to calculate mean profile using np.nanmean.
    
    If minimum lines set, only returns averages for profile blocks with
    more than minimum lines
    
    :arr: 2D array
    :minimum_lines: minimum number of lines to calculate profile for
    '''
    assert arr.ndim == 2, 'Expects 2D array'
    
    with warnings.catch_warnings():
        warnings.filterwarnings(action='ignore', message='Mean of empty slice')
        profile_average = np.nanmean(arr, axis=0)
    
    if minimum_lines:
        num_valid = np.isfinite(arr).sum(axis=0)
        profile_average = np.where(num_valid > minimum_lines, profile_average, np.nan) 
        
    return profile_average

    
def get_range_profiles(arr, azimuth_window=200, minimum_lines=50):
    '''Prepares sigma0 or NESZ image for noise scaling.
    
    Range profile averages are calculated for consecutive, non-overlapping 
    windows in the azimuth direction.  Window size is defined by azimuth_window.
    Averages are not returned for windows with less than minimum_lines valid lines.
    
    :arr: a 2D array with azimuth direction along axis=0 and range direction along axis=1
    :azimuth_window: size of non-overlapping window to use for averaging
    :minimum_lines: minimum number of valid lines
    '''
    
    assert arr.ndim == 2, 'Expects a 2D array'
    
    nline, npixel = arr.shape  # nline is number of azimuth lines, npixel number of pixels in range

    window_start = np.arange(0, nline, azimuth_window)
    window_end = window_start + 200
    window_end = np.where(window_end > nline, nline, window_end)

    lines = np.floor( (window_start + window_end)/2. )
    
    arr_average = []
    for w0, w1 in zip(window_start, window_end):
        if w1 - w0 > minimum_lines:
            arr_average.append(range_profile_average(arr[w0:w1, :]))
            
    return arr_average, lines


def get_block_variance(s0, n0, k):
    '''
    Calculates variance of residual noise
    
    :s0: azimuth mean profile of sigma0
    :n0: azimuth mean profile of NESZ
    :p: pixel index
    :k: noise scaling factor
    '''
    n0_scaled = k * n0
    offset = np.nanmean(s0) - np.nanmean(n0_scaled)
    n0_shifted = n0_scaled + offset
    s0_var = np.nanvar(s0 - n0_shifted)
    return s0_var
