"""Extracts calibrated radar backscatter, noise vectors and geolocation to a geotiff"""

import sys
sys.path.append('..')  #/heS1denoise')

import warnings
from pathlib import Path

from heS1denoise.sentinel1image import S1Image


DATAPATH = Path('/media', 'apbarret', 'andypbarrett_work', 'Data',
                'ExtremeEarthPolar', 'Images', 'Original')

images = [
    'S1A_EW_GRDM_1SDH_20180116T075430_20180116T075530_020177_0226B9_9FE3',
    'S1B_EW_GRDM_1SDH_20180213T175444_20180213T175544_009608_011511_8266',
    'S1A_EW_GRDM_1SDH_20180313T181225_20180313T181325_021000_0240E1_8163',
    'S1A_EW_GRDM_1SDH_20181016T072958_20181016T073058_024158_02A460_DA8F',
    'S1B_EW_GRDM_1SDH_20181113T074529_20181113T074629_013583_019254_D382',
    ]


def main():

    for image_base in images:
        print(DATAPATH / f'{image_base}.zip')


if __name__ == "__main__":
    main()
