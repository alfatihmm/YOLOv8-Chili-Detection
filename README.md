# YOLOv8 Chili Detection 🌶️
Real-time chili (pepper) object detection using YOLOv8 (Ultralytics), featuring FPS measurement, basic object tracking, model evaluation, and optional Google Sheets/Drive integration.

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?logo=python&logoColor=white)
![Ultralytics](https://img.shields.io/badge/Ultralytics-YOLOv8-00C3FF?logo=ultralytics&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Real--time%20CV-5C3EE8?logo=opencv&logoColor=white)

---

## Table of Contents
- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Repository Structure](#repository-structure)
- [Requirements & Installation](#requirements--installation)
- [Quick Start](#quick-start)
- [Train a Model (Optional)](#train-a-model-optional)
- [Evaluation & Analysis](#evaluation--analysis)
- [Google Sheets/Drive Integration (Optional)](#google-sheetsdrive-integration-optional)
- [Performance Tips](#performance-tips)
- [FAQ](#faq)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Project Overview
This project uses YOLOv8 to detect chili peppers in images and videos. Beyond prediction, it includes:
- Real-time performance (FPS) measurement
- Basic object tracking
- Reporting (PDF) and visualization
- Automated logging to Google Sheets
- Utility functions related to distance/location

---

## Key Features
- Real-time chili detection powered by YOLOv8
- FPS measurement and performance visualization
- Basic object tracking
- Model evaluation (confusion matrix)
- Export results to PDF
- Optional Google Sheets and Google Drive integrations for logging/archiving
- Ready-to-use notebooks for quick experimentation

---

## Repository Structure
- `mainfix.py` — Main detection/inference pipeline script.
- `detecthitungfps.py` — Detection with FPS calculation and logging.
- `tracker.py` — Object tracking utilities.
- `jaraklok.py` — Distance/location-related utilities.
- `botsheet.py`, `fungsisheet.py` — Google Sheets integration and helpers.
- `fungsidrive.py` — Google Drive integration (upload/download).
- `fungsipdf.py` — PDF report generation.
- `CustomDatasetYOLOv8.ipynb` — Notebook to set up/train a custom dataset.
- `confusionmatrix (1).ipynb` — Notebook to compute and analyze a confusion matrix.
- `grafikfps.ipynb` — Notebook to visualize performance (FPS).
- `coco1.txt` — Class/label list (COCO-like or custom classes).

Note: File names reflect their responsibilities; open each file for implementation details.

---

## Requirements & Installation
Python 3.9+ is recommended.

1) Create and activate a virtual environment (optional but recommended)
```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

2) Install core dependencies
```bash
pip install ultralytics opencv-python numpy pandas matplotlib
```

3) Optional dependencies by feature
```bash
# Google Sheets/Drive
pip install gspread oauth2client google-api-python-client

# PDF reporting
pip install reportlab

# Extra visualization/analytics
pip install seaborn scikit-learn
```

If you already have trained weights (e.g., `best.pt`), place them under `weights/` or adjust the script arguments accordingly.

---

## Quick Start
1) Run inference on image/video with a script
```bash
# Replace paths as needed
python detecthitungfps.py --source path/to/video_or_image --weights weights/best.pt --conf 0.25
```

2) Run the main pipeline
```bash
python mainfix.py --source path/to/input --weights weights/best.pt --conf 0.25
```

3) Quick inference via Ultralytics CLI (alternative)
```bash
yolo task=detect mode=predict model=weights/best.pt source=path/to/input conf=0.25
```

Common parameters:
- `--source`: path to an image, folder, or video (use `0` for the default webcam).
- `--weights`: trained YOLOv8 weights (`.pt`).
- `--conf`: detection confidence threshold (0–1).

---

## Train a Model (Optional)
Use `CustomDatasetYOLOv8.ipynb` to:
- Prepare a custom dataset
- Configure data and class files (see `coco1.txt` if relevant)
- Train a YOLOv8 model and export `best.pt`

CLI example:
```bash
yolo task=detect mode=train model=yolov8n.pt data=path/to/data.yaml epochs=50 imgsz=640
```

---

## Evaluation & Analysis
- Confusion matrix: open `confusionmatrix (1).ipynb` to generate and analyze the confusion matrix from validation results.
- FPS visualization: use `grafikfps.ipynb` to plot performance (FPS) from logs produced by `detecthitungfps.py`.

---

## Google Sheets/Drive Integration (Optional)
- Google Sheets:
  - Files: `botsheet.py`, `fungsisheet.py`
  - Create a Service Account in Google Cloud Console
  - Download the credentials JSON and set the env var `GOOGLE_APPLICATION_CREDENTIALS` to the JSON path
  - Share your Google Sheet with the service account email

- Google Drive:
  - File: `fungsidrive.py`
  - Use the same credentials (or as implemented)
  - Ensure the Drive API is enabled in your GCP project

- PDF Reports:
  - File: `fungsipdf.py`
  - Export detections/analytics to PDF for documentation.

---

## Performance Tips
- Use a lighter model (e.g., `yolov8n.pt`) for higher FPS on limited hardware.
- Set `imgsz` to 640 or smaller to speed up inference.
- Prefer GPU (CUDA) if available for significant acceleration.
- Lower `conf` only when needed to capture small/low-confidence objects (may increase false positives).

---

## FAQ
- Where should I place model weights?
  - Put them at `weights/best.pt` or use `--weights` to point to a custom path.

- How do I add new classes?
  - Update your training data `.yaml` and adapt the class list (see `coco1.txt` if used).

- Can I use a webcam?
  - Yes. Set `--source 0`.

---

## Contributing
Contributions are welcome!
1) Fork this repository
2) Create a feature/bugfix branch
3) Open a pull request with a clear description

---

## License
No license file was found in this repository. Consider adding a LICENSE file to define usage rights.

---

## Acknowledgements
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- The open-source CV/ML community
