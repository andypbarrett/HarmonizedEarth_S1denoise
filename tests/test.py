from pathlib import Path

from heS1denoise.sentinel1image import S1Image


DATAPATH = Path('/media', 'apbarret', 'andypbarrett_work', 'Data', 'Sentinel1_Sun')
IMAGEPATH = DATAPATH / 'S1A_EW_GRDM_1SDH_20180902T165032_20180902T165132_023522_028FAA_35D2.zip'


s1 = S1Image(str(IMAGEPATH))
print(s1)

