"""Extracts calibrated radar backscatter, noise vectors and geolocation to a geotiff"""

import sys
sys.path.append('..')  #/heS1denoise')

import warnings
from pathlib import Path

import numpy as np

from heS1denoise.sentinel1image import S1Image
from nansat import Nansat


DATAPATH = Path('/media', 'apbarret', 'andypbarrett_work', 'Data',
                'ExtremeEarthPolar', 'Images')

images = [
    'S1A_EW_GRDM_1SDH_20180116T075430_20180116T075530_020177_0226B9_9FE3',
    'S1B_EW_GRDM_1SDH_20180213T175444_20180213T175544_009608_011511_8266',
    'S1A_EW_GRDM_1SDH_20180313T181225_20180313T181325_021000_0240E1_8163',
    'S1A_EW_GRDM_1SDH_20181016T072958_20181016T073058_024158_02A460_DA8F',
    'S1B_EW_GRDM_1SDH_20181113T074529_20181113T074629_013583_019254_D382',
    ]


def get_parameters(s1, band_id):
    """Wrapper to get parameters for a given band"""
    if band_id in ['incidence_angle', 'sigma0_HH', 'sigma0_HV']:
        parameters = s1.get_metadata(band_id=band_id)
        for i in ['dataType', 'PixelFunctionType', 'SourceBand', 'SourceFilename']:
            if i in parameters:
                parameters.pop(i)
    #elif band_id in ['nesz_HH', 'nesz_HV']:
    #    parameters = s1.get_metadata(band_id=band_id.replace('nesz', 'noise'))
    #    for i in ['dataType', 'PixelFunctionType', 'SourceBand', 'SourceFilename']:
    #        if i in parameters:
    #            parameters.pop(i)
    else:
        parameters = {'short_name': band_id.upper()}
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

    
def to_geotiff(image_path, output_path, output_type=np.float32, verbose=False):
    """Extracts sigma0 for HH, HV, incidence angle and NESZ"""
    print(f'Opening {image_path}')
    try:
        s1 = S1Image(image_path)
    except Exception as err:
        print(f'Failed to open {image_path}')
        print(err)
        return

    n = Nansat.from_domain(s1)

    bands = ['incidence_angle', 'sigma0_HH', 'sigma0_HV', 'nesz_HH', 'nesz_HV']

    for band in bands:
        if verbose: print(f'   Getting {band}')
        arr = get_band(s1, band)
        params = get_parameters(s1, band)
        n.add_band(array=arr.astype(output_type), parameters=params)

    n.set_metadata(s1.get_metadata())

    if verbose: print(f'Writing data to {output_path}')
    n.export(str(output_path), driver='GTiff')


def main(verbose=False):

    for image_base in images:
        image_path = DATAPATH / 'Original' / f'{image_base}.zip'
        output_path = DATAPATH / 'GeoTIFF' / f'{image_base}.tif'
        to_geotiff(image_path, output_path, verbose=verbose)
        break


if __name__ == "__main__":
    main(verbose=True)
