# scripts/1_change_format.py
import glob
import shutil
from pathlib import Path

# ใช้ alias จาก config ให้ตรงกับสคริปต์เดิม
from config import SRC_ROOT, SRC_IMG, SRC_LBL, DST_ROOT, DST_IMG, DST_LBL

# ---------- PARAMS ----------
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}
KEEP_UNLABELED = False  # True = เก็บรูปที่ไม่มี label ไว้ด้วย (ปกติแนะนำ False)

def main():
    # ----- PREP DEST -----
    DST_IMG.mkdir(parents=True, exist_ok=True)
    DST_LBL.mkdir(parents=True, exist_ok=True)

    # ----- COLLECT FILES -----
    imgs = [
        Path(p) for p in glob.glob(str(SRC_IMG / "**/*"), recursive=True)
        if Path(p).suffix.lower() in IMG_EXTS
    ]
    lbls = [Path(p) for p in glob.glob(str(SRC_LBL / "**/*.txt"), recursive=True)]

    # mapping label ตามชื่อไฟล์ (ไม่รวมสกุล)
    lbl_by_key = {p.stem: p for p in lbls}

    # ----- COPY FILES -----
    copied_imgs = 0
    copied_lbls = 0
    missing_lbl = []

    for img in imgs:
        key = img.stem
        lbl = lbl_by_key.get(key)

        # copy image เสมอ
        shutil.copy2(img, DST_IMG / img.name)
        copied_imgs += 1

        # copy label ถ้ามี
        if lbl and lbl.is_file():
            shutil.copy2(lbl, DST_LBL / lbl.name)
            copied_lbls += 1
        else:
            # ถ้าไม่อยากเก็บรูปที่ไม่มี label → ลบภาพออก
            if not KEEP_UNLABELED:
                try:
                    (DST_IMG / img.name).unlink(missing_ok=True)
                    copied_imgs -= 1
                except Exception:
                    pass
            missing_lbl.append(img.name)

    # ----- CREATE train.txt -----
    train_txt_path = DST_ROOT / "train.txt"
    with open(train_txt_path, "w") as f:
        for p in sorted(DST_IMG.glob("*")):
            if p.suffix.lower() in IMG_EXTS:
                f.write(str(p) + "\n")

    # ----- CREATE data.yaml (ชี้ไป /content/<DST_ROOT.name>/...) -----
    # ตรงกับดีไซน์เดิมของคุณเป๊ะ (ค่าใน Colab)
    dataset_name = DST_ROOT.name
    base = f"/content/{dataset_name}"
    train_dir = f"{base}/train/images"
    valid_dir = f"{base}/valid/images"   # โฟลเดอร์ชื่อ valid ได้ แต่ key ใน YAML ต้องเป็น 'val'
    test_dir  = f"{base}/test/images"

    yaml_path = DST_ROOT / "data.yaml"
    yaml_text = f"""names:
- food
- snack
- drink
- glass
- person
nc: 5
train: {train_dir}
val: {valid_dir}
test: {test_dir}
"""
    with open(yaml_path, "w") as f:
        f.write(yaml_text)

    # ----- SUMMARY -----
    print("✅ change_format done.")
    print(f"Images copied: {copied_imgs}")
    print(f"Labels copied: {copied_lbls}")
    if missing_lbl:
        print(f"⚠️ Images without label: {len(missing_lbl)} e.g. {missing_lbl[:5]}")
    print("Output root:", DST_ROOT)
    print("train.txt   :", train_txt_path)
    print("data.yaml   :", yaml_path)

if __name__ == "__main__":
    main()
