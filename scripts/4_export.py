import os, shutil, zipfile
from pathlib import Path
from config import SPLIT_PATH, AUGMENTED_PATH, EXPORT_ROOT

FINAL_DIR = EXPORT_ROOT   # โฟลเดอร์สุดท้ายก่อน zip

# ---------- CLEAN FINAL DIR ----------
if FINAL_DIR.exists():
    shutil.rmtree(FINAL_DIR)
FINAL_DIR.mkdir(parents=True, exist_ok=True)

# ---------- MERGE ORIGINAL + AUGMENTED ----------
def merge_split(split):
    src_img1 = SPLIT_PATH / split / "images"
    src_lbl1 = SPLIT_PATH / split / "labels"
    src_img2 = AUGMENTED_PATH / split / "images"
    src_lbl2 = AUGMENTED_PATH / split / "labels"
    dst_img  = FINAL_DIR / split / "images"
    dst_lbl  = FINAL_DIR / split / "labels"
    dst_img.mkdir(parents=True, exist_ok=True)
    dst_lbl.mkdir(parents=True, exist_ok=True)

    # copy original
    if src_img1.exists():
        for f in src_img1.glob("*"):
            shutil.copy2(f, dst_img/f.name)
    if src_lbl1.exists():
        for f in src_lbl1.glob("*"):
            shutil.copy2(f, dst_lbl/f.name)

    # copy augmented
    if src_img2.exists():
        for f in src_img2.glob("*"):
            shutil.copy2(f, dst_img/f.name)
    if src_lbl2.exists():
        for f in src_lbl2.glob("*"):
            shutil.copy2(f, dst_lbl/f.name)

    print(f"📂 Merged split {split}: {len(list(dst_img.glob('*')))} images")

# ใช้ train/valid/test เหมือนเดิม
for split in ["train", "valid", "test"]:
    merge_split(split)

# ---------- COPY data.yaml ----------
yaml_src = SPLIT_PATH / "data.yaml"
yaml_dst = FINAL_DIR / "data.yaml"
if yaml_src.exists():
    shutil.copy2(yaml_src, yaml_dst)
    print(f"✅ Copied data.yaml -> {yaml_dst}")
else:
    print("⚠️ WARNING: data.yaml not found in split folder")

# ---------- ZIP ----------
zip_path = str(EXPORT_ROOT) + ".zip"
all_files = [p for p in FINAL_DIR.rglob("*") if p.is_file()]
total = len(all_files)
print(f"📦 Preparing to zip {total} files -> {zip_path}")

with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for i, file in enumerate(all_files, 1):
        arcname = file.relative_to(FINAL_DIR)
        zipf.write(file, arcname)
        percent = (i/total)*100
        print(f"\r⏳ Zipping... {percent:.1f}% ({i}/{total})", end="")

print(f"\n✅ Exported: {zip_path}")
