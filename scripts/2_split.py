import os, glob, shutil, random
from pathlib import Path
from config import SRC_IMG, SRC_LBL, SPLIT_PATH  # ใช้ SPLIT_PATH จาก config.py

SEED = 42
R_TRAIN, R_TEST, R_VAL = 0.7, 0.2, 0.1   # 70/20/10
IMG_EXTS = {".jpg",".jpeg",".png",".bmp",".tif",".tiff",".webp"}

# ---------- PREP DEST ----------
if SPLIT_PATH.exists():
    shutil.rmtree(SPLIT_PATH)

# โฟลเดอร์ใช้ชื่อ 'valid' ตามที่ต้องการ
for split in ["train", "test", "valid"]:
    (SPLIT_PATH/split/"images").mkdir(parents=True, exist_ok=True)
    (SPLIT_PATH/split/"labels").mkdir(parents=True, exist_ok=True)

# ---------- COLLECT & MATCH ----------
imgs = [Path(p) for p in glob.glob(str(SRC_IMG/"**/*"), recursive=True)
        if Path(p).suffix.lower() in IMG_EXTS]
lbls = [Path(p) for p in glob.glob(str(SRC_LBL/"**/*.txt"), recursive=True)]
lbl_by_key = {p.stem: p for p in lbls}

pairs = []
missing_lbl = []
for img in imgs:
    lab = lbl_by_key.get(img.stem)
    if lab and lab.is_file():
        pairs.append((img, lab))
    else:
        missing_lbl.append(img.name)

# ---------- SHUFFLE & SPLIT ----------
random.seed(SEED)
random.shuffle(pairs)

n = len(pairs)
n_train = int(n * R_TRAIN)
n_test  = int(n * R_TEST)
n_val   = n - n_train - n_test  # ส่วนที่เหลือเป็น valid

train_pairs = pairs[:n_train]
test_pairs  = pairs[n_train:n_train+n_test]
val_pairs   = pairs[n_train+n_test:]

def copy_pairs(pairs, split):
    di = SPLIT_PATH/split/"images"
    dl = SPLIT_PATH/split/"labels"
    for img, lab in pairs:
        shutil.copy2(img, di/img.name)
        shutil.copy2(lab, dl/lab.name)

copy_pairs(train_pairs, "train")
copy_pairs(test_pairs,  "test")
copy_pairs(val_pairs,   "valid")  # <- โฟลเดอร์ชื่อ valid

# ---------- WRITE data.yaml ----------
train_dir = (SPLIT_PATH/"train"/"images").as_posix()
valid_dir = (SPLIT_PATH/"valid"/"images").as_posix()  # <- path ไป valid
test_dir  = (SPLIT_PATH/"test"/"images").as_posix()

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
with open(SPLIT_PATH/"data.yaml", "w") as f:
    f.write(yaml_text)

# ---------- SUMMARY ----------
def count_files(split, sub):
    return len(list((SPLIT_PATH/split/sub).glob("*")))

print("✅ Split done.")
print(f"Total pairs: {n}  | missing labels: {len(missing_lbl)}")
if missing_lbl:
    print("⚠️ e.g.", missing_lbl[:5])
print(f"train: {len(train_pairs)} imgs, labels = {count_files('train','images')}, {count_files('train','labels')}")
print(f"test : {len(test_pairs)} imgs, labels = {count_files('test','images')}, {count_files('test','labels')}")
print(f"valid: {len(val_pairs)} imgs, labels = {count_files('valid','images')}, {count_files('valid','labels')}")  # <- ใช้คำว่า valid
print("Output root:", SPLIT_PATH)
print("data.yaml   :", SPLIT_PATH/'data.yaml')
