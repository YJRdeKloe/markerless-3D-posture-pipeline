# Markerless 3D Posture Estimation Pipeline

This document provides a full workflow for preparing, calibrating, sampling, annotating, and exporting multi-camera datasets for markerless 3D posture estimation using HybridNet + JARVIS tooling.

It includes:

* Folder structure requirements
* MATLAB stereo calibration export
* YAML parameter formatting for each camera
* Multi-entity project YAML structure
* K-means sampling script usage
* Annotation Tool workflow (JARVIS)
* CSV structure and annotation guidelines

---

## 1. Overview of the Pipeline

This workflow is developed for **markerless 3D posture estimation in developmental research**, specifically tested with **toddlers**, but fully applicable to **infants** and, when needed, their **parents or caregivers**. It is written for **developmental experimental psychologists and researchers** who may not have extensive technical or engineering backgrounds. The aim is to provide a clear, step-by-step guide for generating research‑grade 3D posture data from synchronized multi‑camera recordings.

Because this documentation is aimed at researchers in developmental science, explanations are intentionally thorough, with explicit instructions for calibration, folder structures, annotation, and data handling.

Additionally, note the following practical distinction:

* **Stationary laboratory setup:** Cameras remain fixed in place → **calibration only needs to be performed once** (unless cameras are moved).
* **Mobile or semi-mobile setup:** Cameras are transported, mounted temporarily, or re-positioned → **calibration must be redone for every new setup**.

This ensures accurate triangulation and prevents geometric errors in 3D reconstruction.

This workflow is developed for **markerless 3D posture estimation in developmental research**, specifically tested with **toddlers**, but fully applicable to **infants** and, when needed, their **parents or caregivers**. It supports multi-entity annotation (e.g., child + parent) and multi-camera setups (preferably three cameras) to enable robust 3D reconstruction of naturalistic movement.
This pipeline processes synchronized multi-camera recordings (typically **three cameras**, but it also works with two).
This pipeline processes synchronized multi-camera recordings (**three cameras are recommended: left, center, right**), e.g., *left*, *center*, *right*, but also compatible with two-camera setups) into a training-ready annotation dataset for 2D pose estimation.

**Complete workflow:**

1. **Record synchronized calibration videos** using an **asymmetric checkerboard**.
2. **Calibrate cameras in MATLAB** (stereo calibration).
3. **Export intrinsics, distortion coefficients, rotation (R) and translation (T)** for each camera.
4. **Create YAML files for each camera** (`left.yaml`, `right.yaml`).
5. **Record synchronized test videos** of the child + parent.
6. **Create an info YAML file** (e.g., `Try_out.yaml`) specifying:

   * entities (child, parent)
   * keypoints per entity
   * camera list
   * calibration location
7. **Run the K-means sampling script** to generate frame subsets.
8. **Open dataset in JARVIS Annotation Tool**.
9. **Annotate all selected frames**.
10. **Export training set** through JARVIS.

---

## 2. Folder Structure per Test Subject

Each subject folder must contain (example shown for **three cameras**, with the center camera as anchor):

```
SubjectFolder/
    CalibrationParameters/
    left.yaml
    center.yaml
    right.yaml
Videos/
    left.mp4
    center.mp4
    right.mp4
Try_out.yaml)
    annotation_dataset/   ← created by sampling script
```

### Contents:

* **CalibrationParameters/** → Camera intrinsics + extrinsics.
* **Videos/** → Synchronized recordings for each camera, filenames matching YAML names.
* **Try_out.yaml** → Multi-entity, multi-camera project file.
* **annotation_dataset/** → created after K-means sampling, contains:

  * one folder per camera (`left/`, `right/`)
  * extracted frame images
  * an `annotations.csv` in each folder

---

## 3. MATLAB Stereo Calibration

Use MATLAB’s **Camera Calibrator** → **Stereo Camera Calibrator**.

Important outputs you must copy manually:

* **Intrinsic matrix**
* **Radial/tangential distortion**
* **Rotation and translation of Camera 2 relative to Camera 1**

### Example MATLAB commands

```
load('calibrationSession.mat');
calibrationSession.CameraParameters.CameraParameters1.Intrinsics
calibrationSession.CameraParameters.CameraParameters2.Intrinsics
calibrationSession.CameraParameters.RotationOfCamera2
calibrationSession.CameraParameters.TranslationOfCamera2
```

### Choosing the main camera

* If two cameras are used (less preferred): choose one as the **main/anchor** (typically the *left* camera).
* R and T in the *right* YAML describe **Camera 2 relative to Camera 1**.
* For **three cameras (preferred configuration)**:
* Use **three synchronized videos**: `left`, `center`, `right`.
* Choose the **center camera** as the *main/anchor* camera.
* Perform **two stereo calibrations** in MATLAB:

  * center → left
  * center → right
* This results in two sets of extrinsics:

  * `R_left`, `T_left` relative to the center camera
  * `R_right`, `T_right` relative to the center camera
* The center camera receives:

  * `R = identity`
  * `T = [0, 0, 0]`:
  * middle → left
  * middle → right

---

## 4. Camera Calibration YAML Files

Each camera has its own YAML file in OpenCV format.

For a **three-camera setup** with the **center camera as anchor**, you will typically have:

* `left.yaml`   → left camera, extrinsics relative to center
* `center.yaml` → center/anchor camera, identity R and zero T
* `right.yaml`  → right camera, extrinsics relative to center

### Example: `center.yaml` (anchor camera)

This camera defines the world coordinate system. Its rotation is the identity matrix and translation is zero.

```yaml
%YAML:1.0
---
intrinsicMatrix: !!opencv-matrix
   rows: 3
   cols: 3
   dt: d
   data: [ 2.3445e+03, 0., 0., 
           0., 2.3278e+03, 0., 
           1.0002e+03, 0.7456e+03, 1. ]
distortionCoefficients: !!opencv-matrix
   rows: 1
   cols: 5
   dt: d
   data: [ 0.8183, -1.5926, 0., 0., 0. ]
R: !!opencv-matrix
   rows: 3
   cols: 3
   dt: d
   data: [ 1., 0., 0., 
           0., 1., 0., 
           0., 0., 1. ]
T: !!opencv-matrix
   rows: 3
   cols: 1
   dt: d
   data: [ 0., 0., 0. ]
```

### Example: `left.yaml` and `right.yaml`

For the non-anchor cameras, the intrinsics and distortion coefficients come from their respective `cameraIntrinsics` objects in MATLAB. The rotation `R` and translation `T` are taken from the stereo calibration where the **center camera** is Camera 1 and the other camera is Camera 2. In those YAMLs:

* `R` = `RotationOfCamera2` (3×3 matrix)
* `T` = `TranslationOfCamera2` (3×1 vector)

---

## 5. Project Information YAML (`Try_out.yaml`)

This YAML defines the annotation project.

It includes:

* Entities (child, parent)
* Keypoints per entity
* Camera names
* Calibration directory
* Video directory
* Output frame sampling parameters

---

## 6. K-means Sampling Script

Run:

```
python k_means_sampling_updated_multiple.py
```

### Prompts and meaning

* **Base folder** → subject folder containing Videos and CalibrationParameters.
* **num_frames** → total frames to sample **per camera**.
* **n_clusters** → must divide `num_frames` exactly (script ensures equal cluster selection).
* **Main camera index** → must match your MATLAB anchor camera (0 = left, 1 = right).

### Output

Creates:

```
annotation_dataset/
    left/
        Frame_XXX.jpg
        annotations.csv
    right/
        Frame_XXX.jpg
        annotations.csv
```

---

## 7. Annotation CSV Format

Each `annotations.csv` follows **DeepLabCut multi-animal style**, but with state instead of likelihood.

### Header rows:

```
Scorer
entities
bodyparts
coords
```

### Column structure

For each entity:

```
keypoint_1_x, keypoint_1_y, keypoint_1_state,
keypoint_2_x, keypoint_2_y, keypoint_2_state,
...
```

### State values

* **1** = visible / labeled
* **0** = occluded / not visible

---

## 8. Loading the Dataset in JARVIS Annotation Tool

Steps (with screenshots in repo):

### 1. Open Annotation Tool

Choose **Annotate Dataset**.

### 2. Select Dataset

Load the project YAML (`Try_out.yaml`).

### 3. Select Segment

Choose:

```
annotation_dataset
```

### 4. Verify Camera Order

Matches your YAML:

```
left
right
```

### 5. Load Dataset

Workspace opens.

---

## 9. Annotating Frames

Inside the annotation interface:

* Switch between **child** and **parent** entities
* Select keypoints from the right panel
* Mark their location in the image
* Use reprojection view for consistency

Navigation buttons:

* **Next >>**, **Previous**, **Crop**, **Pan**, **Home**

Annotate **both cameras** for each selected frame set.

---

## 10. Export Training Set

After annotating:
Use **Export Trainingset** in the tool.
This produces:

* Training-ready 2D keypoint labels
* Files compatible with HybridNet/JARVIS training
* Correct folder structure for triangulation

---

## Troubleshooting Guide

### 1. Synchronization Errors

Accurate 3D reconstruction is only possible when all cameras are **perfectly synchronized**. Even a **single-frame offset** between cameras will cause:

* Large jumps in triangulated keypoints
* Extremely high reprojection error in the JARVIS Annotation Tool
* Inconsistent or unstable 3D trajectories

**How to detect this:**

* While annotating, enable the **Reprojection** view in JARVIS.
* If synchronization is off, the projected keypoints will appear misaligned or jumping between frames.

**Solutions:**

* Confirm frame indexing during video export.
* Use hardware synchronization when possible.
* For software-based synchronization, align cameras using audio spikes, clapperboard motion, or a bright flash.
* Re-export videos ensuring identical start points.

---

### 2. YAML Formatting Errors

The JARVIS tool is extremely strict about YAML syntax. A **single misplaced comma**, missing bracket, wrong indentation, or malformed OpenCV matrix will cause JARVIS to:

* Crash immediately when loading
* Load cameras incorrectly
* Fail to display frames or calibration
* Reject the project without a visible error message

**Checklist before loading YAMLs:**

* All matrices must be wrapped in `!!opencv-matrix` blocks.
* Commas must be correctly placed inside lists.
* `rows`, `cols`, and `dt` must match the matrix.
* Ensure `R` is 3×3 and `T` is 3×1.
* Quotes are not required for numbers.
* No trailing commas at the end of lists.

If something fails, validate your YAML using an online YAML validator (e.g. yamllint) and compare to the examples provided in this manual.

---

### 3. Calibration Errors (MATLAB)

Poor calibration leads to inaccurate 3D posture estimation. Common issues:

* Checkerboard origin flips between frames
* Blurry images or partial board visibility
* Insufficient spread of board poses (e.g., only center of room)

**Solutions:**

* Remove problematic image pairs using MATLAB’s GUI.
* Ensure checkerboard is visible to all cameras simultaneously.
* Capture poses with wide variation: tilt, rotate, move board through space.

---

## Prerequisites

Before running this pipeline, install or prepare:

* **MATLAB** with the Computer Vision Toolbox (for calibration)
* **Python 3.9+**
* Required Python libraries (NumPy, OpenCV, scikit-learn)
* **JARVIS Annotation Tool**, available here:
  [https://jarvis-mocap.github.io/jarvis-docs/manual/6_creating_and_labeling_datasts/](https://jarvis-mocap.github.io/jarvis-docs/manual/6_creating_and_labeling_datasts/)
* A multi-camera recording setup (preferably 3 cameras)
* Asymmetric checkerboard for calibration

---

## Quick Start

1. Record synchronized calibration videos.
2. Calibrate in MATLAB → export R, T, intrinsics.
3. Create camera YAML files (`left.yaml`, `center.yaml`, `right.yaml`).
4. Record synchronized experimental videos.
5. Create project YAML (`Example_Child_1.yaml`).
6. Run K-means sampling script.
7. Annotate in JARVIS.
8. Export training set.

---

## Citing This Workflow

If you publish research using this pipeline, please cite:

* The **JARVIS Toolkit** (from the JARVIS documentation)
* Any relevant HybridNet or markerless 3D estimation papers
* This repository (once published)

---

## Example YAML Files

This repository includes example calibration YAMLs and an example experiment configuration YAML to help users set up their own projects.

You can find them in the repository under:

```
examples/
    calibration/
        left.yaml
        center.yaml
        right.yaml
    project/
        Try_out.yaml
```

To link to these files directly from this manual, use:

* **[Example center.yaml](../examples/calibration/center.yaml)**
* **[Example left.yaml](../examples/calibration/left.yaml)**
* **[Example right.yaml](../examples/calibration/right.yaml)**
* **[Example Try_out.yaml](../examples/project/Try_out.yaml)**

These example files show the exact formatting required by the JARVIS Annotation Tool, including:

* Correct OpenCV matrix structure
* Proper indentation and syntax
* Required fields for calibration and experiment configuration

Ensure you update the paths, camera names, keypoints, and entities to match your own project.

---

## Additional Resources

For annotation and dataset export, this pipeline uses the **JARVIS Annotation Tool**. The tool, download links, and official documentation can be found here:

**[https://jarvis-mocap.github.io/jarvis-docs/manual/6_creating_and_labeling_datasts/](https://jarvis-mocap.github.io/jarvis-docs/manual/6_creating_and_labeling_datasts/)**

This external manual provides additional instructions on using the annotation interface, project creation, exporting training sets, and troubleshooting.

# END OF DOCUMENT
