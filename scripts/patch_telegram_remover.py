import os
import glob
import re

# === CONFIG ===
SCRIPT_DIR = "scripts"
OUTPUT_DIR = "patched_scripts"
TELEGRAM_PATTERN = [
    r"from telegram_notifier import .*",
    r"send_telegram_message\(.*?\)",
    r"send_top_predictions\(.*?\)",
    r"send_training_report\(.*?\)",
    r"send_retrain_report\(.*?\)",
    r"send_watchdog_alert\(.*?\)",
    r"send_cycle_report\(.*?\)",
    r"send_paper_trading_report\(.*?\)"
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def patch_script(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    modified = False
    patched_lines = []
    for line in lines:
        stripped = line.strip()
        if any(re.search(pattern, stripped) for pattern in TELEGRAM_PATTERN):
            patched_lines.append(f"# [TELEGRAM REMOVED] {line}")
            modified = True
        else:
            patched_lines.append(line)

    if modified:
        out_path = os.path.join(OUTPUT_DIR, os.path.basename(file_path))
        with open(out_path, 'w', encoding='utf-8') as f:
            f.writelines(patched_lines)
        print(f"✅ Patch applicata a: {os.path.basename(file_path)}")
    else:
        print(f"↪️  Nessuna modifica in: {os.path.basename(file_path)}")

def main():
    files = glob.glob(os.path.join(SCRIPT_DIR, "*.py"))
    for script in files:
        patch_script(script)

if __name__ == "__main__":
    main()
