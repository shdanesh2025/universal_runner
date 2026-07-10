# F:/universal_runner/src copy/main.py
import asyncio
import traceback
from env_config import get_config
from asset_manager import prepare_environment

async def main():
    print("=====================================================================")
    print("🚀 INITIALIZING UNIVERSAL RUNNER ENGINE")
    print("=====================================================================")
    
    # 1. Prepare environment dynamically (Mounts drive, extracts if needed)
    prepare_environment()
    
    # 2. Get active configuration
    cfg = get_config()
    
    # Import Orchestrator AFTER setup to ensure paths exist in sys.path
    from pipeline_core.engine import Orchestrator

    # 3. Launch the engine
    try:
        orchestrator = Orchestrator(cfg)
        await orchestrator.run()
        print("\n✅ Execution Complete.")
    except Exception as e:
        print(f"\n❌ Pipeline halted: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
