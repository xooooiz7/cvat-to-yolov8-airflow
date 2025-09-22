# cvat-to-yolov8-airflow

Automated data pipeline with **Apache Airflow** for converting CVAT annotations to YOLOv8 format.  
Includes DAGs, validation, reporting, and reproducible workflows.

---

## Features
- Convert CVAT XML/ZIP → YOLOv8 (detection/segmentation)
- Automated **Airflow DAG** with clear tasks:
  - Unzip dataset
  - Validate annotation format
  - Convert to YOLOv8 format
  - Train/Val/Test split
  - Data augmentation
  - Export final dataset + summary report
- **Idempotent**: safe to re-run without overwriting
- Generates dataset summary (per-class counts, missing labels, etc.)

---

## Project Structure
```
cvat-to-yolov8-airflow/
├─ dags/                 # Airflow DAG definition
│   └─ snackvision_dag.py
├─ scripts/              # Python scripts for each task
│   ├─ 1_change_format.py
│   ├─ 2_split.py
│   ├─ 3_augment.py
│   ├─ 4_export.py
│   ├─ 5_classanalysis.py
│   └─ config.py
├─ data/                 # (ignored) datasets folder
│   ├─ raw/              # CVAT input
│   ├─ unzipped/
│   ├─ split/
│   ├─ yolo_format/      # YOLOv8 output
│   └─ reports/          # dataset summary
├─ requirements.txt
└─ .gitignore
```

---

## Quickstart
1. Clone the repo:
   ```bash
   git clone https://github.com/xooooiz7/cvat-to-yolov8-airflow.git
   cd cvat-to-yolov8-airflow
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start Airflow (example with docker-compose):
   ```bash
   docker-compose up
   ```

4. Access Airflow UI → trigger DAG: **`cvat_to_yolov8`**

---

## Example DAG


---

## Sample Report
```
{
  "summary": {
    "images_total": 242,
    "labels_total": 218,
    "missing_labels": 5
  },
  "class_distribution": {
    "food": 120,
    "drink": 80,
    "snack": 42
  }
}
```

---

## Next Steps
- Add unit tests for converters
- Support polygon segmentation
- Auto-trigger YOLOv8 training after export
- CI/CD integration for reproducibility
