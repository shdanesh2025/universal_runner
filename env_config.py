# F:/universal_runner/src copy/env_config.py
import os
import sys
from dotenv import load_dotenv

# Load local .env variables if the file exists
load_dotenv()

# ==========================================
# 1. AUTO-DETECT ENVIRONMENT
# ==========================================
if "google.colab" in sys.modules:
    CURRENT_ENV = "colab"
elif os.environ.get("GITHUB_ACTIONS") == "true":
    CURRENT_ENV = "github"
else:
    CURRENT_ENV = "local"

# ==========================================
# 2. ENVIRONMENT PROFILES
# ==========================================
ENV_PROFILES = {
    "colab": {
        "MOUNT_GDRIVE": True,
        "FEED_DIR": "/content/drive/MyDrive/gemini_input",
        "OUT_DIR": "/content/drive/MyDrive/gemini_output",
        "BASE_WORK_DIR": "/content",
        "LOCAL_WORKDIR": "/content/local_prompts_workspace",
        "LOCAL_RESPONSES_DIR": "/content/local_responses"
    },
    "local": {
        "MOUNT_GDRIVE": False,
        "FEED_DIR": "./content" if os.path.exists("./content") else ".", 
        "OUT_DIR": "./output", 
        "BASE_WORK_DIR": ".",
        "LOCAL_WORKDIR": ".", 
        "LOCAL_RESPONSES_DIR": "./output/local_responses"
    },
    "github": {
        "MOUNT_GDRIVE": False,
        "FEED_DIR": "./content" if os.path.exists("./content") else ".", 
        "OUT_DIR": "./output", 
        "BASE_WORK_DIR": ".",
        "LOCAL_WORKDIR": ".", 
        "LOCAL_RESPONSES_DIR": "./output/local_responses"
    }
}

ACTIVE_PROFILE = ENV_PROFILES[CURRENT_ENV]

# Ensure relative module imports work seamlessly across environments
if ACTIVE_PROFILE["LOCAL_WORKDIR"] not in sys.path:
    sys.path.append(ACTIVE_PROFILE["LOCAL_WORKDIR"])

# ==========================================
# 3. SECRETS LOADER
# ==========================================
def get_api_keys() -> list:
    keys = []
    env_keys = os.environ.get("GEMINI_API_KEYS", "")
    if env_keys:
        keys = [k.strip() for k in env_keys.split(",") if k.strip()]
        
    if not keys and CURRENT_ENV == "colab":
        try:
            from google.colab import userdata
            colab_key = userdata.get("GEMINI_API_KEY")
            if colab_key: 
                keys = [colab_key]
        except Exception:
            pass
            
    if not keys:
        print("❌ Error: No API keys configured in environment or secrets.")
        return []
    return keys

def get_zip_password() -> str:
    pwd = os.environ.get("ZIP_PASSWORD", "")
    if not pwd and CURRENT_ENV == "colab":
        try:
            from google.colab import userdata
            pwd = userdata.get("ZIP_PASSWORD") or ""
        except Exception: pass
    return pwd

# ==========================================
# 4. GLOBAL CONFIGURATION
# ==========================================
GLOBAL_CONFIG = {
    "PIPELINE_CONFIG_FILENAME": "project_disease_gen/pipeline_config.json",
    "SELECTED_MODEL": "gemini-3.1-flash-lite",
    "CHECKPOINT_INTERVAL": 5,
    "PERIODIC_CHECKPOINT_INTERVAL": 300,
    "MAX_RETRIES": 3,
    "AUTO_TUNE_CONCURRENCY": False,
    "CONCURRENT_REQUEST_SIZE": 1,
    "KEY_RPM_LIMIT": 2,
    "KEY_DAILY_LIMIT": 500,
    "KEY_TPM_LIMIT": 250000,
    "MAX_RESPONSE_TOKENS": 65000,
    "GET_MIDDLE_STEPS_BACKUP": True,
    "RETRY_FAILED_ITEMS": True,
    "THINKING_BUDGET": -1,
    "THINKING_LEVEL": "High",
    "CURRENT_PHASE": 1,
    "TOTAL_PHASES": 1,
    "LOCAL_WORKDIR": ACTIVE_PROFILE["LOCAL_WORKDIR"],
    "LOCAL_RESPONSES_DIR": ACTIVE_PROFILE["LOCAL_RESPONSES_DIR"],
    "GDRIVE_OUTPUT_DIR": ACTIVE_PROFILE["OUT_DIR"],
    "API_KEYS": get_api_keys(),
    "ZIP_PASSWORD": get_zip_password()
}

def get_config():
    return GLOBAL_CONFIG
