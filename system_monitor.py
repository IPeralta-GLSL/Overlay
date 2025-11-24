import psutil
import datetime
import subprocess
import shutil

class SystemMonitor:
    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=None)

    def get_ram_usage(self):
        return psutil.virtual_memory().percent

    def get_gpu_usage(self):
        if shutil.which("nvidia-smi"):
            try:
                output = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                return float(output.decode("utf-8").strip())
            except Exception:
                pass
        return 0.0

    def get_current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")
