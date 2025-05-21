# Registration pipeline for projecting an atlas from adult fsaverage to dhcp neonates

The current pipeline uses a surface based registration process 

### Required software and python packages
FSL
AFNI
ANTS
FreeSurfer
NiLearn

### Organization
The registration pipeline follows a multi-step sequence to create the necessary files for registration and atlas projection

The dhcp_params.py file has all the directory files. Adjust these to your system prior to running

The registration_pipeline.py file executes the registration process by sequentially running different steps of the registration

Each step of the registration is set up as a seperate script in the fmri folder

The registration process is tracked in the participants_dhcp.csv file. This file should have all participants with usable functional/structural data, but update for you needs as necessary.

Atlases should be in surface space as a .1D.dset file type
    *check afni documentation for help 
    https://afni.nimh.nih.gov/pub/dist/doc/program_help/ConvertDset.html
    https://afni.nimh.nih.gov/pub/dist/doc/program_help/ROI2dataset.html


### Running the registration

All steps of the registration are run from the registration_pipeline.py

1. in your participants csv, set the to_run column to 1 for the participants you want to run the registration for
2. in registration_pipeline.py set which group you want to run registration for. Currently this supports dhcp infants and 7T HCP adults (look at params file)
3. set the atlas or roi you want to register. 
    *Note, only atlas uses the rigorous surface registration. 
4. set the flags for which registration steps to run. For the first time running, you will want to the following to true: extract_brain, reg_phase1, reg_phase2, reg_phase3, register_atlas, split_atlas
    *screenshots of the atlas registration for each participant will be saved under fmri/qc I recommend scrolling through these and checking that the registration looks right
5. Once those are finished (probably < 30 mins per participant), set the extract_ts_roi flag to True. This will extract the ROI average time series from each ROI in your atlas. This step takes a lot longer and so I recommend running it seperately

It's possible to run some of these processes in parallel by setting the batch_job flag to True, but I would be careful doing this until you have a good understanding of the pipeline. In general, I only use it for the last time series step since that's the slowest


### If you use this please cite:
Ayzenberg, V., Song, C., & Arcaro, M. J. (2025). An intrinsic hierarchical, retinotopic organization of visual pulvinar connectivity in the human neonate. Current Biology, 35(2), 300-314.
