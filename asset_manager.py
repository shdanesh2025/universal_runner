# F:/universal_runner/src copy/asset_manager.py
import os
import shutil
import tempfile
import sys
import importlib
import pyzipper
from env_config import CURRENT_ENV, ACTIVE_PROFILE, get_config

def find_file(filename, fallback_dir):
    path = os.path.join(ACTIVE_PROFILE["BASE_WORK_DIR"], filename)
    if os.path.exists(path): return path
    fallback = os.path.join(fallback_dir, filename) if fallback_dir else None
    if fallback and os.path.exists(fallback): return fallback
    return None

def extract_encrypted_zip(zip_path, dest_dir, password):
    with pyzipper.AESZipFile(zip_path, 'r') as zf:
        if password:
            zf.setpassword(password.encode('utf-8'))
        zf.extractall(dest_dir)

def prepare_environment():
    if ACTIVE_PROFILE["MOUNT_GDRIVE"]:
        try:
            from google.colab import drive
            drive.mount('/content/drive')
        except Exception as e: 
            print(f"Drive mount failed: {e}")

    os.makedirs(ACTIVE_PROFILE["LOCAL_WORKDIR"], exist_ok=True)
    os.makedirs(ACTIVE_PROFILE["LOCAL_RESPONSES_DIR"], exist_ok=True)
    os.makedirs(ACTIVE_PROFILE["OUT_DIR"], exist_ok=True)

    print("📦 Detecting zipped assets...")
    feed = ACTIVE_PROFILE["FEED_DIR"]
    core_path = find_file("pipeline_core.zip", feed)
    prompts_path = find_file("prompts_package.zip", feed)
    assets_path = find_file("assets.zip", feed)
    
    pwd = get_config()["ZIP_PASSWORD"]

    dest_core = os.path.join(ACTIVE_PROFILE["LOCAL_WORKDIR"], "pipeline_core")
    if not os.path.exists(dest_core) and core_path:
        print("📦 Unpacking pipeline_core...")
        os.makedirs(dest_core, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            extract_encrypted_zip(core_path, td, pwd)
            contents = os.listdir(td)
            src_dir = os.path.join(td, "pipeline_core") if len(contents) == 1 and contents[0] == "pipeline_core" else td
            for f in os.listdir(src_dir): shutil.move(os.path.join(src_dir, f), os.path.join(dest_core, f))

    dest_prompts = os.path.join(ACTIVE_PROFILE["LOCAL_WORKDIR"], "project_disease_gen")
    if not os.path.exists(dest_prompts) and prompts_path:
        print("📦 Unpacking prompts_package...")
        extract_encrypted_zip(prompts_path, ACTIVE_PROFILE["LOCAL_WORKDIR"], pwd)

    dest_assets = os.path.join(ACTIVE_PROFILE["LOCAL_WORKDIR"], "assets")
    if not os.path.exists(dest_assets) and assets_path:
        print("📦 Unpacking assets...")
        os.makedirs(dest_assets, exist_ok=True)
        with tempfile.TemporaryDirectory() as td:
            extract_encrypted_zip(assets_path, td, pwd)
            contents = os.listdir(td)
            src_dir = os.path.join(td, "assets") if len(contents) == 1 and contents[0] == "assets" else td
            for f in os.listdir(src_dir): shutil.move(os.path.join(src_dir, f), os.path.join(dest_assets, f))

    if not os.path.exists(os.path.join(ACTIVE_PROFILE["LOCAL_WORKDIR"], "pipeline_core")):
        print("\n❌ CRITICAL ERROR: The 'pipeline_core' engine directory was not found. Please ensure pipeline_core.zip is in the root directory or already unpacked.")
        sys.exit(1)

    for module_name in list(sys.modules.keys()):
        if module_name == "pipeline_core" or module_name.startswith("pipeline_core."):
            sys.modules.pop(module_name, None)
    importlib.invalidate_caches()
