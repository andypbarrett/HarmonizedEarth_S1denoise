"""Extracts calibrated radar backscatter, noise vectors and geolocation to a geotiff"""

import sys
sys.path.append('..')  #/heS1denoise')

import warnings
from pathlib import Path

from heS1denoise.sentinel1image import S1Image
from nansat import Nansat


DATAPATH = Path('/media', 'apbarret', 'andypbarrett_work', 'Data',
                'ExtremeEarthPolar', 'Images', 'Original')

images = [
    'S1A_EW_GRDM_1SDH_20180116T075430_20180116T075530_020177_0226B9_9FE3',
    'S1B_EW_GRDM_1SDH_20180213T175444_20180213T175544_009608_011511_8266',
    'S1A_EW_GRDM_1SDH_20180313T181225_20180313T181325_021000_0240E1_8163',
    'S1A_EW_GRDM_1SDH_20181016T072958_20181016T073058_024158_02A460_DA8F',
    'S1B_EW_GRDM_1SDH_20181113T074529_20181113T074629_013583_019254_D382',
    ]


def get_parameters(s1, band_id):
    """Wrapper to get parameters for a given band"""
    parameters = s1.get_metadata(band_id='incidence_angle')
    for i in ['dataType', 'PixelFunctionType', 'SourceBand', 'SourceFilename']:
        if i in parameters:
            parameters.pop(i)
    return parameters


def get_band(s1, band_id):
    """Returns a band as an array"""
    if band_id in ['incidence_angle', 'sigma0_HH', 'sigma0_HV']:
        arr = s1[band_id]
    elif band_id in ['nesz_HH', 'nesz_HV']:
        pol = band_id.split('_')[1]
        arr = s1.get_nesz_full_size(pol)
    else:
        raise KeyError(f'Unexpected band_id: {band_id}')
    return arr

    
def to_geotiff(image_path, verbose=False):
    """Extracts sigma0 for HH, HV, incidence angle and NESZ"""
    try:
        s1 = S1Image(image_path)
    except Exception as err:
        print(f'Failed to open {image_path}')
        print(err)

    n = Nansat.from_domain(s1)

    if verbose: print('   Getting incidence_angle')
    arr = get_band(s1, 'incidence_angle')
    params = get_parameters(s1, 'indicence_angle')
    print(arr.min(), arr.max())
    print(arr.shape)
    print(params)
    
    #if verbose: print('   Getting sigma0 for HH')
    #sigma0_hh = s1['sigma0_HH']

    #if verbose: print('   Getting sigma0 for HV')
    #sigma0_hv = s1['sigma0_HV']

    #if verbose: print('   Getting NESZ for HH')
    #nesz_hh = s1.get_nesz_full_size('HH')

    #if verbose: print('   Getting NESZ for HV')
    #nesz_hv = s1.get_nesz_full_size('HV')
    

    #n.export(args.ofile, driver='GTiff')


def main(verbose=False):

    for image_base in images:
        image_path = DATAPATH / f'{image_base}.zip'
        print(f'Opening {image_path}')
        to_geotiff(image_path, verbose=verbose)
        break


if __name__ == "__main__":
    main(verbose=True)
