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
- Idempotent: safe to re-run without overwriting
- Generates dataset summary (per-class counts, missing labels, etc.)

---

## Project Structure

cvat-to-yolov8-airflow/
├─ dags/ # Airflow DAG definition
│ └─ snackvision_dag.py
├─ scripts/ # Python scripts for each task
│ ├─ 1_change_format.py
│ ├─ 2_split.py
│ ├─ 3_augment.py
│ ├─ 4_export.py
│ ├─ 5_classanalysis.py
│ └─ config.py
├─ data/ # (ignored) datasets folder
│ ├─ raw/ # CVAT input
│ ├─ unzipped/
│ ├─ split/
│ ├─ yolo_format/ # YOLOv8 output
│ └─ reports/ # dataset summary
├─ requirements.txt
└─ .gitignore
