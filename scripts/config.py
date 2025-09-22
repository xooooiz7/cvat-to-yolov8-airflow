from pathlib import Path
import yaml

# ----- PROJECT ROOT -----
PROJECT_ROOT = Path("/Users/sittasahathum/Desktop/airflow_snackvision")

# ----- PIPELINE PATHS -----
# Input จาก CVAT ที่แตกไฟล์แล้ว
RAW_PATH         = PROJECT_ROOT / "data" / "raw"

# Output step 1: รวมเป็น YOLO-format (ยังไม่ split)
YOLO_FORMAT_PATH = PROJECT_ROOT / "data" / "yolo_format"

# Output step 2: ชุดที่ split แล้ว (ใช้เทรน/วิเคราะห์จริง)
SPLIT_PATH       = PROJECT_ROOT / "data" / "split"

# Output step 3: รูป augment เพิ่ม
AUGMENTED_PATH   = PROJECT_ROOT / "data" / "augmented"

# Output step 4: รวมชุดพร้อมส่ง/zip
EXPORT_ROOT      = PROJECT_ROOT / "data" / "final_export"

# รายงาน/ไฟล์สถิติ
REPORT_PATH      = PROJECT_ROOT / "data" / "reports"

# data.yaml หลักที่ใช้เทรน (จะถูกสร้างโดยสคริปต์ split)
DATA_YAML = SPLIT_PATH / "data.yaml"


def load_yolo_data_yaml(path: Path = DATA_YAML):
    """
    โหลดข้อมูลจาก data.yaml แบบปลอดภัย
    - ถ้าไฟล์ยังไม่ถูกสร้าง ให้คืนค่า default ว่าง ๆ กลับไป
    """
    if not path.exists():
        return {"train": None, "val": None, "test": None, "names": [], "nc": 0}

    with open(path, "r") as f:
        y = yaml.safe_load(f)

    names_field = y.get("names", [])
    if isinstance(names_field, dict):
        names = [names_field[k] for k in sorted(names_field)]
    else:
        names = list(names_field)

    return {
        "train": y.get("train"),
        "val": y.get("val"),
        "test": y.get("test"),
        "names": names,
        "nc": y.get("nc", len(names)),
    }


# ===== Aliases สำหรับสคริปต์รุ่นเดิม (ที่อ้าง SRC_*/DST_* ) =====
# Source จาก CVAT (โครงสร้าง: raw/images/Train , raw/labels/Train)
SRC_ROOT = RAW_PATH
SRC_IMG  = SRC_ROOT / "images" / "Train"
SRC_LBL  = SRC_ROOT / "labels" / "Train"

# ปลายทางแบบ pre-split (ยังไม่แยก train/valid/test)
DST_ROOT = YOLO_FORMAT_PATH
DST_IMG  = DST_ROOT / "images"
DST_LBL  = DST_ROOT / "labels"
