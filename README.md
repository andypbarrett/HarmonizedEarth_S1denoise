<p align="center">
  <img alt="NSIDC logo" src="https://nsidc.org/themes/custom/nsidc/logo.svg" width="150" height="150" />
  <img alt="NSF logo" src="https://nsidc.org/sites/default/files/images/Logo/NSF.svg" width="150" height="150" />
</p>

[![NSF-2026962](https://img.shields.io/badge/NSF-2026962-red.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=2026962)

# HarmonizedEarth_S1denoise

A python package that applys Sun et al (2021) denoising algorithm the Sentinel-1 SAR imagery.

Y. Sun and X. -M. Li, "Denoising Sentinel-1 Extra-Wide Mode Cross-Polarization Images Over Sea Ice," in IEEE Transactions on Geoscience and Remote Sensing, vol. 59, no. 3, pp. 2116-2131, March 2021, doi: 10.1109/TGRS.2020.3005831.

The package is built on the Nansen Centers S1denoise package, which is used to load  
Sentinel-1 SAFE files, and extract image and noise vectors.  The original Sun et al code was written in Matlab, available on [Zenodo](https://zenodo.org/record/4558740#.YvrpX9LMLCI).
The original Matlab code has been translated into python and modified to improve speed and functionality.

This work is under development.
