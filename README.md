# Latent Dynamical Modeling of fMRI to Probe Brain-Wide Effects of Ultrasound Sonication in Tremor

## Overview

Tremor is one of the most disabling and treatment-resistant symptoms of Parkinson's disease (PD). Low-intensity focused ultrasound (LiFUS) has emerged as a promising non-invasive neuromodulation approach for reducing tremor, but the brain-wide mechanisms through which focal sonication of a single region influences distributed motor networks remain poorly understood.

This project applies **BRICK** (BRain dynamics Identification using Control and Koopman operator) — a deep learning framework based on Koopman operator theory — to resting-state fMRI data collected before and after LiFUS sonication in PD patients. Rather than treating brain activity as a static network, BRICK models BOLD signals as a time-evolving dynamical system, transforming complex nonlinear brain dynamics into a tractable linear representation in a learned latent space.

**Hypothesis:** Focal LiFUS sonication produces statistically significant changes in one or more latent dynamical modes identified by the Koopman framework, consistent with a distributed reconfiguration of motor and tremor-related brain networks, rather than a purely localized effect.

## Data

Data are from Vuong, Sreenivasan et al. (2026), *"Low-intensity transcranial ultrasound effects on the ventral intermediate nucleus and zona incerta in Parkinson's disease tremor,"* Brain Stimulation, and are publicly available on [OSF](https://osf.io/fhqwd/overview). The dataset consists of ROI-averaged resting-state BOLD time series (VIM and ZI targets, 22 additional cerebello-thalamo-cortical ROIs) collected pre- and post-TUS in 19 PD participants.


## Project structure

```
├── data/            # Raw and processed fMRI data (the OSF dataset, link included)
├── preprocessing/   # Scripts for cleaning, parcellation, formatting time series
├── models/          # BRICK architecture: Koopman linearization, spatio-temporal encoder, control module
├── training/        # Training loops, configs, checkpoints
├── analysis/        # Statistical comparison of latent modes, pre/post effects
├── results/         # Figures, tables, model outputs (not tracked in git)
├── scripts/         # Scripts of general purpose tasks like filename parsing and data overview
├── tests/           # Unit tests (pytest)
├── requirements.txt
└── README.md
```
