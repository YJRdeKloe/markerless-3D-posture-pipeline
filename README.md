# Markerless 3D Posture Estimation Pipeline

This repository provides a complete workflow for preparing, calibrating, sampling, annotating, and exporting multi-camera datasets for markerless 3D posture estimation using HybridNet and the JARVIS Annotation Tool.

The pipeline was originally developed and validated in the context of developmental science, as part of the study:

> **De Kloe, Y. J. R., Hunnius, S., & Stapel, J. S.**
> *Markerless 3D Posture Estimation of Toddlers from Multi-View Video Recordings: Evaluating Accuracy, Precision, and Generalizability.* (Under review)

The workflow supports 3D posture estimation in toddlers, infants, caregivers, and other multi-entity movement contexts.

---

## Documentation

The full pipeline documentation is located here:

### **[`docs/pipeline_manual.md`](docs/pipeline_manual.md)**

It includes:

* Folder structure requirements
* Camera calibration workflow (MATLAB → OpenCV YAML)
* YAML formatting rules
* Multi-camera project configuration
* K-means frame-selection
* Annotation workflow in JARVIS
* Calibration and synchronization troubleshooting
* Export instructions for training

---

## Repository Structure

```plaintext
markerless-3D-posture-pipeline/
│
├── docs/
│   └── pipeline_manual.md
│
├── examples/
│   ├── calibration/
│   │   ├── left.yaml
│   │   ├── middle.yaml
│   │   └── right.yaml
│   └── project/
│       └── Example_Child_1.yaml
│
├── scripts/
│   └── kmeans_frame_selection.py
│
└── README.md
```

---

## Running the K-means Sampling Script

From the repository root:

```bash
python scripts/kmeans_frame_selection.py
```

The script prompts for:

* Base directory (per subject)
* Number of framesets
* Number of clusters
* Main camera index

It outputs an `annotation_dataset/` folder ready for annotation in JARVIS.

---

## Requirements

* Python 3.9+
* NumPy, OpenCV, scikit-learn
* MATLAB with Computer Vision Toolbox
* JARVIS Annotation Tool:
  [https://jarvis-mocap.github.io/jarvis-docs/manual/6_creating_and_labeling_datasts/](https://jarvis-mocap.github.io/jarvis-docs/manual/6_creating_and_labeling_datasts/)
* Multi-camera recording setup (preferably 3 cameras)
* Asymmetric checkerboard for calibration

---

## TODO (After Publication)

Once the manuscript is published:

* Add the pretrained HybridNet model used in the toddler-lab evaluation (so new users can fine-tune starting from this model rather than training from scratch).

This notice will remain until the model is added.

---

## Citing This Workflow

If you use this workflow or codebase, please cite:

```
De Kloe, Y. J. R., Hunnius, S., & Stapel, J. S. (under review).  
Markerless 3D Posture Estimation of Toddlers from Multi-View Video Recordings: Evaluating Accuracy, Precision, and Generalizability.
```

and the official JARVIS Toolkit documentation.
