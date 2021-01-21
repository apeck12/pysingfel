#!/usr/bin/env python
# coding: utf-8

########## LCLS-II Autoranging Detector ###############
# In this notebook, we demonstrate the LCLS-II autoranging detector effect by varying the characteristics of the beam, the type of the detector and its camera configuration.

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from pysingfel import *
import pysingfel as ps
from pysingfel.util import asnumpy, xp
from pysingfel.build_autoranging_frames import BuildAutoRangeFrames

# Input files
input_dir='../input'
beamfile=input_dir+'/beam/amo86615.beam'
geom=input_dir+'/lcls/amo86615/PNCCD::CalibV1/Camp.0:pnCCD.1/geometry/0-end.data'
pdbfile=input_dir+'/pdb/3iyf.pdb'

# Load beam
beam = ps.Beam(beamfile)
increase_factor = 1e5
print('BEFORE: # of photons per pulse = {}'.format(beam.get_photons_per_pulse()))
print('>>> Increasing the number of photons per pulse by a factor {}'.format(increase_factor))
beam.set_photons_per_pulse(increase_factor*beam.get_photons_per_pulse())
print('AFTER : # of photons per pulse = {}'.format(beam.get_photons_per_pulse()))
#beam._n_phot = 1e14 # detector normal
#beam._n_phot = 1e17 # detector saturates
#beam._n_phot = 1e20 # detector gets fried

# Load and initialize the detector
det = ps.Epix10kDetector(geom=geom, run_num=0, beam=beam, cameraConfig='fixedMedium')
increase_factor = 0.5
print('BEFORE: detector distance = {} m'.format(det.distance))
print('>>> Increasing the detector distance by a factor of {}'.format(increase_factor))
det.distance = increase_factor*det.distance
print('AFTER : detector distance = {} m'.format(det.distance))

# Create particle object(s)
particle = ps.Particle()
particle.read_pdb(pdbfile, ff='WK')

# Perform SPI experiment
tic = time.time()

experiment = ps.SPIExperiment(det, beam, particle)
dp_photons = experiment.generate_image_stack() # generate diffraction field

tau = beam.get_photon_energy()/1000.
dp_keV = dp_photons * tau # convert photons to keV

I0width = 0.03
I0min = 0
I0max = 150000
bauf = BuildAutoRangeFrames(det, I0width, I0min, I0max, dp_keV)
bauf.makeFrame()
calib_photons = bauf.frame / tau # convert keV to photons

toc = time.time()
print(">>> It took {:.2f} seconds to finish SPI calculation.".format(toc-tic))

# Visualization
viz = ps.Visualizer(experiment, diffraction_rings="auto", log_scale=True)
fig = plt.figure()
img = experiment.det.assemble_image_stack(calib_photons)
viz.imshow(img)
plt.show()
