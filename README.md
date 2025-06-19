# Registration Pipeline for Projecting Adult Atlases to DHCP Neonates

This pipeline projects cortical atlases from adult fsaverage space to individual neonate brain space using surface-based registration. The pipeline supports multiple output spaces including anatomical, functional (EPI), and diffusion (DWI) spaces.



## Overview

The registration pipeline transforms cortical atlases defined in adult template space to individual subject spaces through a multi-step process:

1. **Brain extraction and preprocessing** - Prepares anatomical and functional data
2. **Surface-based registration** - Registers individual surfaces to fsaverage template  
3. **Atlas projection** - Projects atlas from template to individual anatomy
4. **Space transformations** - Transforms atlases to functional/diffusion spaces
5. **Data extraction** - Extracts timeseries or connectivity data

## Key Features

- **Surface-based registration** using FreeSurfer and AFNI for accurate cortical alignment
- **Multiple output spaces** - anatomical, functional (EPI), and diffusion (DWI) 
- **Flexible atlas support** - Works with any cortical atlas in surface format
- **Automated pipeline** with dependency tracking and error handling
- **Quality control** outputs for visual inspection of registrations

## Required Software

- **FSL** - Image processing and registration
- **AFNI** - Surface-to-volume projection  
- **ANTs** - Advanced registration tools
- **FreeSurfer** - Surface reconstruction and registration
- **Python packages**: NiLearn, pandas, numpy, nibabel, matplotlib

## Directory Structure

```
dhcp/
├── dhcp_params.py              # Configuration file - EDIT THIS FIRST
├── registration_pipeline.py    # Main pipeline script
├── participants_dhcp.csv       # Subject tracking file
├── fmri/                      # Individual processing scripts
│   ├── extract_brain.py
│   ├── phase1_registration.py
│   ├── phase2_registration.py  
│   ├── phase3_registration.py
│   ├── register_atlas.py
│   ├── split_atlas.py
│   ├── reg_atlas2dwi.py
│   └── qc/                    # Quality control outputs
└── atlases/                   # Atlas directory (configure path in params)
    ├── templates/
    ├── {atlas_name}_lh.1D.dset
    ├── {atlas_name}_rh.1D.dset
    └── {atlas_name}_labels.csv
```

## Quick Start

### 1. Configure Paths
Edit `dhcp_params.py` to set your data directories:
```python
# Update these paths for your system
raw_data_dir = '/path/to/your/dhcp_raw'
out_dir = '/path/to/your/dhcp_preprocessed'  
atlas_dir = '/path/to/your/atlases'
```

**Example for our workstation:**
```python
# Example configuration for our setup
raw_data_dir = '/mnt/DataDrive1/data_raw/human_mri/dhcp_raw'
out_dir = '/mnt/DataDrive1/data_preproc/human_mri/dhcp_preprocessed'
atlas_dir = '/mnt/DataDrive1/data_preproc/human_mri/dhcp_preprocessed/atlases'
```

### 2. Prepare Participants
Update `participants_dhcp.csv` with your subjects and set `to_run=1` for all subjects you want to process. 

The file will updated automatically to tracs which subjects have been processed and which steps are completed.
```csv
participant_id,ses,to_run
sub-CC00056XX07,ses-10700,1,,,,,,,
```

### 3. Decide which steps of the pipeline to run
Edit `registration_pipeline.py` to set which steps you want to run. For a first-time run, set all steps to `True`:
```python

'''
Flags to determine which preprocessing steps to run
'''
#extract brain
extract_brain = True

#Reg-phase1-3 : Register individual anat to fsaverage
reg_phase1 = True
reg_phase2 = True
reg_phase3 = True

#Registers atlas to individual anat
register_atlas = True
#split atlas into individual rois
split_atlas = True

#extracts mean timeseries from each roi of atlas
extract_ts_roi = True

#reg atlas rois to dwi
reg_atlas2dwi = True


```

### 4. Run Pipeline
```bash
python registration_pipeline.py
```

## Detailed Example: Adding a New Atlas

This example shows how to add and run a custom visual areas atlas called "custom_visual".

### Step 1: Prepare Atlas Files

Create your atlas directory structure:
```
/path/to/atlases/
├── custom_visual_lh.1D.dset      # Left hemisphere surface atlas
├── custom_visual_rh.1D.dset      # Right hemisphere surface atlas  
└── custom_visual_labels.csv      # ROI labels and indices
```

**Example for our workstation:**
```
/mnt/DataDrive1/data_preproc/human_mri/dhcp_preprocessed/atlases/
├── custom_visual_lh.1D.dset      # Left hemisphere surface atlas
├── custom_visual_rh.1D.dset      # Right hemisphere surface atlas  
└── custom_visual_labels.csv      # ROI labels and indices
```

**Atlas format requirements:**
- Surface files must be in AFNI `.1D.dset` format on fsaverage surface
- Use AFNI tools to convert: `ConvertDset` or `ROI2dataset`
- See: https://afni.nimh.nih.gov/pub/dist/doc/program_help/ConvertDset.html

**Labels file format:**
```csv
index,label,network
1,V1,early_visual
2,V2,early_visual
3,V3,ventral_visual
4,V4,ventral_visual
```

### Step 2: Add Atlas to Configuration

Edit `dhcp_params.py` and add your atlas to the `load_atlas_info()` class:

```python
class load_atlas_info():
    def __init__(self,atlas):
        
        # ... existing atlases ...
        
        elif atlas == 'custom_visual':
            self.atlas_name = f'custom_visual_hemi'  # 'hemi' will be replaced with lh/rh
            self.roi_labels = pd.read_csv(f'{atlas_dir}/custom_visual_labels.csv')
```

### Step 3: Configure Pipeline

Edit `registration_pipeline.py`:

```python
# Set your new atlas
atlas = 'custom_visual'

# For first-time run (all steps)
extract_brain = True
reg_phase1 = True
reg_phase2 = True  
reg_phase3 = True
register_atlas = True
split_atlas = True

# Optional: extract timeseries
extract_ts_roi = True

# Optional: project to DWI space  
reg_atlas2dwi = True

```

### Step 4: Run Pipeline

```bash
python registration_pipeline.py
```

**Example for our workstation:**
```bash
# Navigate to the project directory
cd /mnt/DataDrive1/git_repos/dhcp

# Run the pipeline
python registration_pipeline.py
```

**Expected runtime:** ~30 minutes per subject for surface registration steps

### Step 5: Verify Outputs

Check quality control images:
```
fmri/qc/custom_visual/infant/{subject}_{session}_custom_visual_epi.png
```

Output ROI files will be created at:
```
{out_dir}/{subject}/{session}/rois/custom_visual/
├── lh_V1_anat.nii.gz    # Anatomical space
├── lh_V1_epi.nii.gz     # Functional space  
├── lh_V1_dwi.nii.gz     # Diffusion space (if reg_atlas2dwi=True)
├── rh_V1_anat.nii.gz
└── ... (all ROIs for both hemispheres)
```

**Example output paths for our workstation:**
```
/mnt/DataDrive1/data_preproc/human_mri/dhcp_preprocessed/sub-CC00056XX07/ses-10700/rois/custom_visual/
├── lh_V1_anat.nii.gz    # Anatomical space
├── lh_V1_epi.nii.gz     # Functional space  
├── lh_V1_dwi.nii.gz     # Diffusion space (if reg_atlas2dwi=True)
├── rh_V1_anat.nii.gz
└── ... (all ROIs for both hemispheres)
```

Output timeseries files will be saved as:
```
{out_dir}/{subject}/{session}/derivatives/timeseries/{sub}_{ses}_{atlas}_{hemi}_ts.npy

# Example: sub-CC00056XX07_ses-10700_custom_visual_lh_ts.npy
```

## Pipeline Dependencies and Rerunning

The pipeline tracks completed steps in `participants_dhcp.csv`. Understanding dependencies helps optimize rerunning:

### Dependency Chain
```
extract_brain → phase_1 → phase_2 → phase_3 → register_atlas → split_atlas → extract_ts_roi
                                                                     ↓
                                                               reg_atlas2dwi
```

### Scenario 1: Adding New Atlas to Existing Subjects

If you've already run the pipeline for atlas 'wang' and want to add 'custom_visual':

```python
# These are already done - set to False
extract_brain = False
reg_phase1 = False
reg_phase2 = False
reg_phase3 = False

# Only run atlas-specific steps  
atlas = 'custom_visual'
register_atlas = True
split_atlas = True
extract_ts_roi = True    # If you want timeseries
reg_atlas2dwi = True     # If you want DWI space
```

**Why this works:** Surface registration (phases 1-3) is atlas-independent, so you only need to rerun atlas-specific steps.

### Scenario 2: Adding DWI Space to Existing Atlas

If you've run 'wang' atlas but want to add DWI space projection:

```python
# Everything else is done
extract_brain = False
reg_phase1 = False
reg_phase2 = False
reg_phase3 = False
register_atlas = False
split_atlas = False

# Only run DWI projection
atlas = 'wang'
reg_atlas2dwi = True
```

### Scenario 3: Rerunning Failed Steps

If a step failed, you can rerun just that step by setting its value to '' (empty) in the CSV file and rerunning with appropriate flags.

## Advanced Configuration

### Parallel Processing

For large datasets, enable parallel processing:

```python
batch_job = True
n_jobs = 10        # Number of parallel jobs
job_time = 20      # Minutes to wait between batches
```

**Warning:** Only use for timeseries extraction steps initially. Surface registration should be run sequentially until you're familiar with the pipeline.

### Multiple Groups

The pipeline supports both infant and adult data:

```python
group = 'infant'   # DHCP neonates
group = 'adult'    # 7T HCP adults
```

### Custom ROI Registration

For volumetric ROIs (not surface-based):

```python
roi = 'pulvinar'
register_vol_roi = True
extract_ts_voxel = True  # Extract voxel-wise timeseries
```

## Quality Control

### Visual Inspection

Always check registration quality using generated images:
```
fmri/qc/{atlas_name}/{group}/{subject}_{session}_{atlas}_epi.png
```

Look for:
- Proper alignment of atlas regions with cortical anatomy
- No obvious misregistrations or artifacts
- Consistent registration quality across subjects

### Log Files

Monitor processing with log files:
```
fmri/qc/preproc_log.txt
```

### Progress Tracking

The pipeline automatically updates `participants_dhcp.csv` with completion status:
- `1` = completed successfully
- `''` (empty) = not yet run or failed

## Troubleshooting

### Common Issues

1. **Missing transform files**
   - Check that all required .mat and .nii.gz transform files exist
   - Verify paths in `dhcp_params.py`

2. **Atlas format errors**  
   - Ensure atlas files are in correct AFNI .1D.dset format
   - Check that hemisphere naming matches ('lh'/'rh')

3. **Memory issues**
   - Reduce `n_jobs` for parallel processing
   - Run timeseries extraction separately with `extract_ts_roi=True` only

4. **Registration failures**
   - Check FreeSurfer installation and SUBJECTS_DIR
   - Verify input data quality and completeness

### Getting Help

- Check log files in `fmri/qc/preproc_log.txt`
- Examine QC images for registration quality
- Verify all software dependencies are properly installed
- Test with a single subject before batch processing

## Output Data

### ROI Files
Individual ROI masks in multiple spaces:
- `{roi}_anat.nii.gz` - Anatomical space
- `{roi}_epi.nii.gz` - Functional space  
- `{roi}_dwi.nii.gz` - Diffusion space

### Timeseries Data
- `{subject}_{session}_{atlas}_{hemi}_ts.npy` - ROI timeseries
- `{subject}_{session}_{atlas}_fc.npy` - Functional connectivity matrix

### Quality Control
- Registration images in `fmri/qc/{atlas}/`
- Processing logs in `fmri/qc/preproc_log.txt`

## Citation

If you use this pipeline, please cite:

Ayzenberg, V., Song, C., & Arcaro, M. J. (2025). An intrinsic hierarchical, retinotopic organization of visual pulvinar connectivity in the human neonate. *Current Biology*, 35(2), 300-314.

## Support

For questions or issues:
1. Check existing documentation and troubleshooting section
2. Examine log files and QC outputs  
3. Test with minimal examples before full dataset processing
4. Ensure all software dependencies are correctly installed