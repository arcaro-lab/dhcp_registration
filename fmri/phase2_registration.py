'''
Phase 2 of registration pipeline: Creates final surfaces and registers to fsaverage
'''
project_name = 'dhcp'
import os
#get current working directory
cwd = os.getcwd()
git_dir = cwd.split(project_name)[0] + project_name
import sys

#add git_dir to path
sys.path.append(git_dir)

import subprocess
import numpy as np
import pandas as pd
from glob import glob as glob
import dhcp_params
import pdb
import shutil

#take subjectand session as command line argument
sub = sys.argv[1]
ses = sys.argv[2]
group = sys.argv[3]

group_info = dhcp_params.load_group_params(group)


#set sub dir
input_dir = f'{group_info.raw_anat_dir}/{sub}/{ses}'
out_dir = f'{group_info.out_dir}/{sub}/{ses}'

anat_suf = group_info.anat_suf


freesurfer_dir = '/usr/local/freesurfer/7.4.1'


for hemi in ['lh','rh']:

    #create freesurfer surfaces with curv info
    print(f'Creating {sub} {ses} {hemi} surfaces')
    bash_cmd = f'mris_smooth -n 5 -nw -seed 1234 {out_dir}/surf/{hemi}.white {out_dir}/surf/{hemi}.smoothwm'
    subprocess.run(bash_cmd.split(), check=True)

    bash_cmd = f'mris_inflate -n 2 {out_dir}/surf/{hemi}.smoothwm {out_dir}/surf/{hemi}.inflated'
    subprocess.run(bash_cmd.split(), check=True)

    bash_cmd = f'mris_curvature -w {out_dir}/surf/{hemi}.white'
    subprocess.run(bash_cmd.split(), check=True)

    bash_cmd = f'mris_curvature -thresh .999 -n -a 5 -w -distances 10 10 {out_dir}/surf/{hemi}.inflated'
    subprocess.run(bash_cmd.split(), check=True)

    bash_cmd = f'mris_sphere {out_dir}/surf/{hemi}.inflated {out_dir}/surf/{hemi}.sphere'
    subprocess.run(bash_cmd.split(), check=True)

    #register to fsaverage and convert back to gifti
    print(f'Registering {sub} {ses} surfaces to fsaverage')
    bash_cmd = f'mris_register {out_dir}/surf/{hemi}.sphere {freesurfer_dir}/average/{hemi}.average.curvature.filled.buckner40.tif {out_dir}/surf/{hemi}.sphere.reg'
    subprocess.run(bash_cmd.split(), check=True)

    bash_cmd = f'mris_convert {out_dir}/surf/{hemi}.sphere.reg {out_dir}/surf/{hemi}.sphere.reg.gii'
    subprocess.run(bash_cmd.split(), check=True)
    

#convert anat to mgz and afni formats
print(f'Converting {sub} {ses} anat to mgz and afni formats')



if os.path.isfile(f'{out_dir}/anat/{sub}_{ses}_{anat_suf}+orig.BRIK'):
    os.remove(f'{out_dir}/anat/{sub}_{ses}_{anat_suf}+orig.BRIK')
    os.remove(f'{out_dir}/anat/{sub}_{ses}_{anat_suf}+orig.HEAD')
 

    

bash_cmd = f'mri_convert {input_dir}/anat/{sub}_{ses}_{anat_suf}.nii.gz {out_dir}/surf/orig.mgz'
subprocess.run(bash_cmd, check=True, shell = True)

bash_cmd = f'3dcopy {input_dir}/anat/{sub}_{ses}_{anat_suf}.nii.gz {out_dir}/anat/{sub}_{ses}_{anat_suf}+orig.nii.gz'
subprocess.run(bash_cmd, check=True, shell = True)

#make orig directory in surf
#needed even if empty
os.makedirs(f'{out_dir}/surf/orig', exist_ok=True)


#run suma make spec
if os.path.isdir(f'{out_dir}/SUMA'):
   shutil.rmtree(f'{out_dir}/SUMA')
    

print(f'Running SUMA_Make_Spec_FS for {sub}')
bash_cmd = f'@SUMA_Make_Spec_FS -fspath {out_dir} -sid {sub}'
subprocess.run(bash_cmd, check=True, shell = True)
