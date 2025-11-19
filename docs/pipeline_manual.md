# Markerless 3D Posture Estimation Pipeline

Markerless 3D Posture Estimation of
Toddlers from Multi-View Video Recordings
Evaluating Accuracy, Precision, and Generalizability

This document provides a complete workflow for preparing, calibrating, sampling, annotating, and exporting multi-camera datasets for markerless 3D posture estimation using HybridNet and JARVIS tooling. It includes:

* Required folder structure
* MATLAB stereo calibration
* YAML parameter formatting for each camera
* Multi-entity project configuration
* K-means sampling workflow
* Annotation Tool usage (JARVIS)
* CSV output structure
* Troubleshooting calibration, synchronization, and YAML issues

The workflow is written for **developmental experimental psychologists and researchers**, especially those working with **infants, toddlers, and their caregivers**, and assumes minimal prior technical background.

---

## 1. Overview of the Pipeline

This workflow was developed and validated in the context of the study:

De Kloe, Y. J. R., Hunnius, S., & Stapel, J. S. (2025). *Markerless 3D Posture Estimation of Toddlers from Multi-View Video Recordings: Evaluating Accuracy, Precision, and Generalizability* (manuscript under review).

### Complete workflow

1. Record synchronized calibration videos using an asymmetric checkerboard.
2. Calibrate cameras in MATLAB.
3. Export intrinsic parameters, distortion coefficients, and extrinsics (R and T).
4. Create camera YAML files (`left.yaml`, `middle.yaml`, `right.yaml`).
5. Record synchronized experimental videos.
6. Create a project YAML file (e.g., `Example_Child_1.yaml`).
7. Run the K-means sampling script to select representative frames.
8. Annotate frames in the JARVIS tool.
9. Export a training set for 2D pose estimation and 3D reconstruction.

### Stationary vs. mobile setups

* **Stationary setup (lab):** Calibration is needed **only once**, unless a camera moves.
* **Mobile or semi-mobile setup:** Calibration must be repeated **every time** the setup is used.

---

## 2. Folder Structure per Test Subject

For a three-camera setup:

```
SubjectFolder/
    CalibrationParameters/
        left.yaml
        middle.yaml
        right.yaml
    Videos/
        left.mp4
        middle.mp4
        right.mp4
    Example_Child_1.yaml
    annotation_dataset/        ← created automatically by sampling script
```

### Notes

* `CalibrationParameters/` contains YAML files describing intrinsic and extrinsic calibration.
* `Videos/` contains synchronized MP4 recordings for each camera.
* `Example_Child_1.yaml` defines entities, keypoints, camera list, and calibration directory.
* `annotation_dataset/` is generated after running the sampling script.

---

## 3. MATLAB Stereo Calibration

Use MATLAB’s **Camera Calibrator** or **Stereo Camera Calibrator** app.

For each stereo pair, export:

* Intrinsic matrix
* Distortion coefficients
* Rotation matrix (`RotationOfCamera2`)
* Translation vector (`TranslationOfCamera2`)

Example MATLAB commands:

```matlab
load('calibrationSession.mat');
calibrationSession.CameraParameters.CameraParameters1.Intrinsics
calibrationSession.CameraParameters.CameraParameters2.Intrinsics
calibrationSession.CameraParameters.RotationOfCamera2
calibrationSession.CameraParameters.TranslationOfCamera2
```

### Three-camera calibration

Use the **middle camera as the anchor**.

Perform two stereo calibrations:

1. Middle → Left
2. Middle → Right

This produces extrinsics:

* `R_left`, `T_left` relative to middle
* `R_right`, `T_right` relative to middle

For the middle camera:

* `R` = identity matrix
* `T` = `[0, 0, 0]`

---

## 4. Camera Calibration YAML Files

Each camera requires a YAML file in OpenCV format.

A three-camera setup includes:

* `middle.yaml`
* `left.yaml`
* `right.yaml`

The **middle camera** defines the coordinate system.

### Example: middle.yaml (anchor camera)

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

---

## Important Note About Example YAML Files

The YAML files included in the `examples/` folder are **templates**. They contain placeholders (e.g., `fx`, `k1`, `R11`, `T1`) instead of real calibration values.

The JARVIS Annotation Tool **will not load these templates**.

To use them:

1. Copy the template YAML.
2. Replace all intrinsic parameters with values from MATLAB.
3. Replace all distortion coefficients.
4. Replace all extrinsic parameters (`R` and `T`) with MATLAB outputs.
5. Save and load the edited version.

This prevents accidental corruption of real calibration files and guides new users clearly.

---

## 5. Project Information YAML (`Example_Child_1.yaml`)

This YAML file defines:

* Entities (child, parent)
* Keypoints for each entity
* Cameras used
* Calibration directory
* Video directory
* Output dataset settings

An example template is provided in `examples/project/Example_Child_1.yaml`.

---

## 6. K-means Sampling Script

The K-means frame selection used in this pipeline is implemented in:

**[`scripts/kmeans_frame_selection.py`](../scripts/kmeans_frame_selection.py)**

Run the script with your favorite python GUI or from the terminal or command window. It will ask you for the base directory per subject (copy paste the entire path), number of frames per camera, number of clusters (must be a division of your number of frames), and the main camera index (must match your anchor camera, usually the index of 'middle')

---

## 7. Annotation CSV Format

### Header rows

```
Scorer
entities
bodyparts
coords
```

### Column structure

For each entity and keypoint:

```
<entity>_<keypoint>_x
<entity>_<keypoint>_y
<entity>_<keypoint>_state
```

### State values

* `1` → keypoint visible
* `0` → keypoint occluded

---

## 8. Loading the Dataset in JARVIS Annotation Tool

1. Open the Annotation Tool.
2. Select **Annotate Dataset**.
3. Select `Example_Child_1.yaml`.
4. Choose segment: `annotation_dataset`.
5. Confirm camera order matches YAML.
6. Load dataset.

---

## 9. Annotating Frames

The interface allows:

* Switching between entities
* Selecting keypoints
* Clicking to mark positions
* Using **Reprojection Mode** to check calibration consistency

Navigation tools:

* **Next**, **Previous**
* **Crop**, **Pan**, **Home**

Annotate all frames in all cameras.

---

## 10. Exporting the Training Set

After annotating:

Follow the steps provided in the [JARVIS Annotation Tool documentation](https://jarvis-mocap.github.io/jarvis-docs/manual/7_training_hybridnet/).

---

## Troubleshooting Guide

### 1. Calibration Errors (MATLAB)

Poor calibration leads to inaccurate 3D posture estimation. Common issues:

* Checkerboard origin flips between frames
* Blurry images or partial board visibility
* Insufficient spread of board poses (e.g., only center of room)

**Solutions:**

* Remove problematic image pairs using MATLAB’s GUI.
* Ensure checkerboard is visible to all cameras simultaneously.
* Capture poses with wide variation: tilt, rotate, move board through space.

### 2. Synchronization Errors

Accurate 3D reconstruction is only possible when all cameras are **perfectly synchronized**. Even a **single-frame offset** between cameras can cause:

* High reprojection error in the JARVIS Annotation Tool
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

### 3. YAML Formatting Errors

The JARVIS tool is extremely strict about YAML syntax. A **single misplaced comma**, missing bracket, wrong indentation, or malformed OpenCV matrix will cause JARVIS to:

* Crash immediately when loading
* Fail to display frames or calibration
* Reject the project without a visible error message

**Checklist before loading YAMLs:**

* All matrices must be wrapped in `!!opencv-matrix` blocks.
* Commas must be correctly placed inside lists.
* `rows`, `cols`, and `dt` must match the matrix.
* Ensure `R` is 3×3 and `T` is 3×1.
* Quotes are not required for numbers.
* No trailing commas at the end of lists.

If something fails, validate your YAML using an online YAML validator and compare to the examples provided in this manual.

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
3. Create camera YAML files (`left.yaml`, `middle.yaml`, `right.yaml`).
4. Record synchronized experimental videos.
5. Create project YAML (`Example_Child_1.yaml`).
6. Run K-means sampling script.
7. Annotate in JARVIS.
8. Export training set.

---

## Citing This Workflow

If you publish research using this pipeline, please cite:

* **De Kloe, Y.J.R.** *Markerless 3D Posture Estimation of Toddlers from Multi-View Video Recordings: Evaluating Accuracy, Precision, and Generalizability* (under review).  
  *This paper introduces, validates, and benchmarks the workflow presented in this repository.*

### BibTeX

```bibtex
@unpublished{deKloe2025markerless3D,
  author       = {De Kloe, Yentl J. R. and Hunnius, Sabine and Stapel, Janny S.},
  title        = {Markerless 3D Posture Estimation of Toddlers from Multi-View Video Recordings: Evaluating Accuracy, Precision, and Generalizability},
  note         = {Manuscript under review},
  year         = {2025}
}
```

* **JARVIS Annotation Tool**, available here:  
  <https://jarvis-mocap.github.io/jarvis-docs/manual/6_creating_and_labeling_datasts/>

* Any relevant HybridNet or markerless 3D estimation papers used in your project

---

## Example YAML Files

This repository includes example calibration YAMLs and an example experiment configuration YAML to help users set up their own projects.

You can find them in the repository under:

```
examples/
    calibration/
        left.yaml
        middle.yaml
        right.yaml
    project/
        Try_out.yaml
```

To link to these files directly from this manual, use:

* **[Example middle.yaml](../examples/calibration/middle.yaml)**
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
