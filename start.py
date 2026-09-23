import os
import sys
import subprocess
import webbrowser

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

def main():
    print("=" * 65)
    print("       MarketAI: Autonomous AI Marketing Campaign Platform")
    print("          B.Tech Major Project • Full-Stack Launcher")
    print("=" * 65)

    # 1. Build frontend
    print("\n[1/2] Compiling React 19 Frontend with Tailwind & Chart.js...")
    try:
        subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, check=True, shell=True)
        print("✓ Frontend bundle compiled successfully!")
    except Exception as e:
        print(f"[Warning] Failed to build frontend with npm: {e}")
        print("Proceeding to launch backend...")

    # 2. Run backend
    print("\n[2/2] Launching MarketAI Full-Stack Server at http://127.0.0.1:5000 ...")
    
    python_bin = os.path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")
    if not os.path.exists(python_bin):
        python_bin = sys.executable

    try:
        webbrowser.open("http://127.0.0.1:5000")
        subprocess.run([python_bin, "app.py"], cwd=BACKEND_DIR)
    except KeyboardInterrupt:
        print("\n[!] MarketAI Server stopped gracefully.")

if __name__ == "__main__":
    main()
