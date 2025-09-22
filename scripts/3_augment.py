# scripts/3_augment.py
import random
import numpy as np
from pathlib import Path
from shutil import copy2
from PIL import Image, ImageEnhance
from config import SPLIT_PATH  # << ใช้ชุด split เป็นแหล่งและปลายทาง "ที่เดียวกัน"

# ====== PATHS (augment in-place ใน split/train) ======
SRC_IMG = SPLIT_PATH / "train/images"
SRC_LBL = SPLIT_PATH / "train/labels"

# OUT = ที่เดิม (in-place augment)
OUT_IMG = SRC_IMG
OUT_LBL = SRC_LBL

# ====== PARAMS ======
SEED = 42
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

AUG_NOISE_PER_IMAGE = 1       # ต่อภาพ: ทำ Gaussian noise 1 รูป
AUG_CONTRAST_PER_IMAGE = 1    # ต่อภาพ: ทำ Contrast 1 รูป

GAUSS_SIGMA_RANGE = (5, 20)   # ความแรง noise
CONTRAST_RANGE    = (0.6, 1.6)

PCT_SELECT = 1.0              # 1.0 = ใช้ทุกภาพฐาน

# ====== UTILS ======
def list_images(folder: Path):
    return [p for p in folder.glob("*") if p.suffix.lower() in IMG_EXTS]

def is_augmented_name(stem: str) -> bool:
    # กันวน augment ซ้ำไฟล์ที่เคยสร้างไว้แล้ว
    return any(s in stem for s in ["_gn", "_ct"])

def load_img(path: Path):
    return Image.open(path).convert("RGB")

def save_img(img, out_path: Path, quality=95):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.suffix.lower() in [".jpg", ".jpeg", ".webp"]:
        img.save(out_path, quality=quality)
    else:
        img.save(out_path)

def stem_with_suffix(p: Path, suffix: str) -> Path:
    return p.with_name(p.stem + suffix + p.suffix)

def yolo_label_for(img_path: Path) -> Path:
    return SRC_LBL / (img_path.stem + ".txt")

def copy_label(src_img: Path, dst_img: Path):
    src_lbl = yolo_label_for(src_img)
    if src_lbl.exists():
        dst_lbl = OUT_LBL / (dst_img.stem + ".txt")
        dst_lbl.parent.mkdir(parents=True, exist_ok=True)
        copy2(src_lbl, dst_lbl)
        return True
    return False

# ====== AUGMENT FUNCS ======
def add_gaussian_noise(im, sigma: float):
    arr = np.array(im).astype(np.float32)
    noise = np.random.normal(0, sigma, arr.shape).astype(np.float32)
    noisy = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy)

def adjust_contrast(im, factor: float):
    return ImageEnhance.Contrast(im).enhance(factor)

# ====== MAIN ======
def main():
    random.seed(SEED)
    np.random.seed(SEED)

    # รูปฐาน (ตัดไฟล์ที่เคย augment ทิ้ง)
    base_imgs = [p for p in list_images(SRC_IMG) if not is_augmented_name(p.stem)]
    total_all = len(base_imgs)
    if total_all == 0:
        print(f"❌ ไม่พบรูปฐานใน {SRC_IMG}")
        return

    k = max(1, int(round(total_all * PCT_SELECT)))
    chosen = random.sample(base_imgs, k)

    print(f"📦 Train images (base): {total_all} | Select ~{PCT_SELECT*100:.0f}% -> {k} images")

    made, missing = 0, 0

    for idx, img_path in enumerate(chosen, 1):
        im = load_img(img_path)

        # ----- GAUSSIAN NOISE -----
        for _ in range(AUG_NOISE_PER_IMAGE):
            sigma = random.uniform(*GAUSS_SIGMA_RANGE)
            im_aug = add_gaussian_noise(im, sigma)
            suffix = f"_gn{int(sigma)}"
            out_img = OUT_IMG / stem_with_suffix(img_path, suffix).name
            save_img(im_aug, out_img)
            if not copy_label(img_path, out_img):
                missing += 1
            made += 1

        # ----- CONTRAST -----
        for _ in range(AUG_CONTRAST_PER_IMAGE):
            factor = random.uniform(*CONTRAST_RANGE)
            im_aug = adjust_contrast(im, factor)
            suffix = f"_ct{int(factor*100)}"
            out_img = OUT_IMG / stem_with_suffix(img_path, suffix).name
            save_img(im_aug, out_img)
            if not copy_label(img_path, out_img):
                missing += 1
            made += 1

        # ---- PROGRESS ----
        percent = (idx / k) * 100
        print(f"\r⏳ Augmenting train... {percent:.1f}% ({idx}/{k})", end="")

    print(f"\n✅ Augment เสร็จ: เพิ่ม {made} รูป (noise + contrast) ลงใน {OUT_IMG}")
    if missing:
        print(f"⚠️ ก๊อป label ไม่ได้ {missing} ไฟล์ (ต้นฉบับไม่มี .txt คู่)")

if __name__ == "__main__":
    main()
