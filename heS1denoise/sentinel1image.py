'''Classes and methods to denoise Sentinel1 images'''

import warnings
from pprint import pprint

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


    def calculate_block_scaling_factors(self, band='HV', zoom_step=1, crop=400,
                                  azimuth_window=200, minimum_lines=50):
        '''Calculates NESZ noise scaling factors following Sun et al, 2021'''
        if self.sigma0.size == 0:
            self.sigma0 = self[self.get_band_number(band_id=f'sigma0_{band}')]
        if self.nesz.size == 0:
            self.nesz = self.get_nesz_full_size(band)
            
        self.block_scaling_factors = block_scaling_factor(self.sigma0,
                                                     self.nesz,
                                                     self.swath_bounds[band],
                                                     zoom_step=zoom_step,
                                                     crop=crop,
                                                     azimuth_window=azimuth_window,
                                                     minimum_lines=minimum_lines)
        self.block_scaling_factors['IPFversion'] = self.IPFversion


    def calculate_swath_scaling_factors(self, variance_threshold=10**-7.1):
        '''Calculates scaling factors for each swath from block scaling factors'''
        self.swath_scaling_factor = {}
        for swath_name, swath_results in self.block_scaling_factors.items():
            if 'IPFversion' in swath_name:
                continue
            self.swath_scaling_factor[swath_name] = \
                calc_swath_scaling_factor(swath_results)

    
    def apply_noise_scaling(self, band='HV'):
        '''Applys scaling factors to NESZ'''
        self.nesz_scaled = get_corrected_nesz(self.nesz,
                                              self.swath_bounds[band],
                                              self.swath_scaling_factor)


    def print_block_scaling_factors(self):
        '''Replace with a json dumps routine to write to a file if necessay'''
        for swath_name, swath_results in self.block_scaling_factors.items():
            if 'IPFversion' in swath_name:
                continue
            print(swath_name)
            print(list(swath_results.keys()))


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
    nlines, npixels = sigma0.shape
    pixel = np.arange(npixels)

    sigma0_average, line = get_range_profiles(sigma0,
                                              azimuth_window=azimuth_window,
                                              minimum_lines=minimum_lines)
    nesz_average, _ = get_range_profiles(nesz,
                                         azimuth_window=azimuth_window,
                                         minimum_lines=minimum_lines)

    # Subsample averages in range direction
    if zoom_step > 1:
        sigma0_average = [s0avg[::zoom_step] for s0avg in sigma0_average]
        nesz_average = [neszavg[::zoom_step] for neszavg in nesz_average]
        pixel = pixel[::zoom_step]
        
    results = {}
    for swath_name, swath_bound in swath_bounds.items():
        results[swath_name] = {
            'sigma0': [],
            'noise_equivalent_sigma0': [],
            'scaling_factor': [],
            'correlation_coefficient': [],
            'fit_residual': [],
            'block_variance': [],
            }

        zipped = zip(
            swath_bound['firstAzimuthLine'],
            swath_bound['lastAzimuthLine'],
            swath_bound['firstRangeSample'],
            swath_bound['lastRangeSample']
            )

        for fal, lal, frs, lrs in zipped:
            valid1 = np.where( (line >= fal) &
                               (line <= lal) )[0]

            for v1 in valid1:
                valid2 = np.where( (pixel >= frs+crop) &
                                   (pixel <= lrs-crop) &
                                   np.isfinite(nesz_average[v1]) )[0]
            
                meanS0 = sigma0_average[v1][valid2]
                meanN0 = nesz_average[v1][valid2]
                pixel_index = pixel[valid2]
            
                (scaling_factor,
                 correlation_coefficient,
                 fit_residual) = fit_noise_scaling_coeff(meanS0, meanN0, pixel_index)

                block_variance = get_block_variance(meanS0, meanN0, scaling_factor)

                results[swath_name]['sigma0'].append(meanS0)
                results[swath_name]['noise_equivalent_sigma0'].append(meanN0)
                results[swath_name]['scaling_factor'].append(scaling_factor)
                results[swath_name]['correlation_coefficient'].append(correlation_coefficient)
                results[swath_name]['fit_residual'].append(fit_residual)
                results[swath_name]['block_variance'].append(block_variance)
                
    return results


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


def calc_swath_scaling_factor(result, variance_threshold = 10**-7.1):
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
    # TODO: make results a class
    scaling_factor = np.array(result['scaling_factor'])
    variance = np.array(result['block_variance'])
    
    small_variance = variance < variance_threshold
    
    if not any(small_variance):
        swath_scaling_factor = np.nanmean(scaling_factor)
    else:
        swath_scaling_factor = np.nanmean( np.where(small_variance, scaling_factor, np.nan) )
        
    return swath_scaling_factor


def get_corrected_nesz(nesz, swath_bounds, scaling_factors):
    '''Apply noise scaling factors to NESZ following s1denoise

    '''
    nesz_corrected = np.array(nesz)

    for swath_name, swath_bound in swath_bounds.items():
        zipped = zip(
            swath_bound['firstAzimuthLine'],
            swath_bound['lastAzimuthLine'],
            swath_bound['firstRangeSample'],
            swath_bound['lastRangeSample']
            )

        for fal, lal, frs, lrs in zipped:
            nesz_corrected[fal:lal+1, frs:lrs+1] *= scaling_factors[swath_name]

    return nesz_corrected
