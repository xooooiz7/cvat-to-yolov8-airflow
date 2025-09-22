# scripts/5_classanalysis.py
import glob, sys
from pathlib import Path
from collections import Counter
from config import SPLIT_PATH  # root = data/split

# ---------------- Utils ----------------
def read_names_from_yaml(yaml_path: Path, max_cls_id: int | None = None):
    names = None
    if yaml_path.exists():
        try:
            import yaml
            with open(yaml_path, "r") as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict) and "names" in data:
                if isinstance(data["names"], list):
                    names = data["names"]
                elif isinstance(data["names"], dict):
                    names = [data["names"][k] for k in sorted(data["names"].keys())]
        except Exception:
            pass
    if names is None:
        if max_cls_id is None:
            return None
        names = [f"class{i}" for i in range(max_cls_id + 1)]
    return names

def parse_label_file(path: Path):
    cls_ids = []
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                t0 = line.split()[0]
                try:
                    cid = int(float(t0))
                    if cid >= 0:
                        cls_ids.append(cid)
                except ValueError:
                    continue
    except Exception:
        pass
    return cls_ids

# --------------- Main analyze ---------------
# ใช้โฟลเดอร์ 'valid' (ไม่ใช่ 'val')
split_folders = [("train","TRAIN"), ("valid","VALID"), ("test","TEST")]

split_stats = {}
overall_obj_counts = Counter()
overall_img_counts = Counter()
max_cls_id_seen = -1

for folder, label in split_folders:
    lbl_dir = SPLIT_PATH / folder / "labels"
    if not lbl_dir.exists():
        print(f"⚠️ Skip: {lbl_dir} not found")
        continue

    files = sorted(glob.glob(str(lbl_dir / "*.txt")))
    obj_counts = Counter()
    img_counts = Counter()
    empty_files = 0

    for fp in files:
        cls_ids = parse_label_file(Path(fp))
        if not cls_ids:
            empty_files += 1
            continue
        obj_counts.update(cls_ids)
        for cid in set(cls_ids):
            img_counts[cid] += 1
            if cid > max_cls_id_seen:
                max_cls_id_seen = cid

    split_stats[folder] = {
        "label": label,
        "n_label_files": len(files),
        "empty_label_files": empty_files,
        "obj_counts": obj_counts,
        "img_counts": img_counts,
    }
    overall_obj_counts.update(obj_counts)
    overall_img_counts.update(img_counts)

# โหลดชื่อคลาส (yaml ใช้ key 'val' แต่ path ใน yaml ชี้ไปโฟลเดอร์ 'valid' อยู่แล้ว)
names = read_names_from_yaml(SPLIT_PATH / "data.yaml", max_cls_id_seen if max_cls_id_seen >= 0 else 0)
if names is None:
    names = [f"class{i}" for i in range(max_cls_id_seen + 1)]

def fmt_row(cix, name, objs, imgs, objs_total):
    pct = (objs / objs_total * 100.0) if objs_total > 0 else 0.0
    return f"{cix:>3}  {name:<15}  objs={objs:<6}  imgs={imgs:<6}  ({pct:5.1f}%)"

print(f"📂 Dataset root: {SPLIT_PATH}")
print("------------------------------------------------------------"); sys.stdout.flush()

for folder, label in split_folders:
    if folder not in split_stats:
        continue
    st = split_stats[folder]
    print(f"\n[{label}] label files={st['n_label_files']} | empty={st['empty_label_files']}")
    objs_total = sum(st["obj_counts"].values())
    if objs_total == 0:
        print("  (no objects)")
        continue

    for cid in range(len(names)):
        cname = names[cid] if cid < len(names) else f"class{cid}"
        objs = st["obj_counts"].get(cid, 0)
        imgs = st["img_counts"].get(cid, 0)
        print(" ", fmt_row(cid, cname, objs, imgs, objs_total))
    sys.stdout.flush()

print("\n==================== OVERALL ====================")
objs_total = sum(overall_obj_counts.values())
print(f"Total objects: {objs_total}")
for cid in range(len(names)):
    cname = names[cid] if cid < len(names) else f"class{cid}"
    objs = overall_obj_counts.get(cid, 0)
    imgs = overall_img_counts.get(cid, 0)
    print(" ", fmt_row(cid, cname, objs, imgs, objs_total))
sys.stdout.flush()
