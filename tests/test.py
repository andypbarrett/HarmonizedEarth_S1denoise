from pathlib import Path

from heS1denoise.sentinel1image import S1Image


DATAPATH = Path('/media', 'apbarret', 'andypbarrett_work', 'Data', 'Sentinel1_Sun')
IMAGEPATH = DATAPATH / 'S1A_EW_GRDM_1SDH_20180902T165032_20180902T165132_023522_028FAA_35D2.zip'


def test_class_init():
    '''Attempts to load image'''
    try:
        s1 = S1Image(IMAGEPATH)
    except:
        print(f'Failed to load {IMAGEPATH}')
        #print(error)
        return
    
    print(s1)
    return s1


def test_arrays_init(s1):
    '''Checks initialized data arrays are empty'''

    assert s1.nesz.size == 0, 'self.nesz is not empty'
    assert s1.nesz_scaled.size == 0, 'self.nesz_scaled is not empty'
    assert s1.sigma0.size == 0, 'self.sigma0 is not empty'
    assert s1.sigma0_denoised.size == 0, 'self.sigma0_denoised is not empty'
    
    print(f'{test_arrays_init.__name__}: nesz, nesz_scaled, sigma0, sigma0_denoised all empty ndarrays')


def test_calc_block_scaling_factor(s1):
    s1.calculate_block_scaling_factors()
    s1.print_block_scaling_factors()


if __name__ == "__main__":
    s1 = test_class_init()
    test_arrays_init(s1)
    test_calc_block_scaling_factor(s1)
