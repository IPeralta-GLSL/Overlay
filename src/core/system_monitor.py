import psutil
import datetime
import subprocess
import shutil
import platform

class SystemMonitor:
    def __init__(self):
        self.cpu_name = self._get_cpu_name()

    def _get_cpu_name(self):
        try:
            if platform.system() == "Windows":
                command = "wmic cpu get name"
                output = subprocess.check_output(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
                return output.split("\n")[1].strip()
            else:
                return platform.processor()
        except:
            return "CPU"

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=None)

    def get_ram_usage(self):
        return psutil.virtual_memory().percent

    def get_gpu_info(self):
        gpus = []
        if shutil.which("nvidia-smi"):
            try:
                names = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode("utf-8").strip().split('\n')
                
                usages = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode("utf-8").strip().split('\n')
                
                for name, usage in zip(names, usages):
                    gpus.append((name.strip(), float(usage.strip())))
            except Exception:
                pass
        
        if not gpus and platform.system() == "Windows":
            try:
                command = "wmic path win32_VideoController get name"
                output = subprocess.check_output(command, shell=True, creationflags=subprocess.CREATE_NO_WINDOW).decode().strip()
                lines = output.split("\n")[1:]
                for line in lines:
                    if line.strip():
                        gpus.append((line.strip(), 0.0))
            except:
                pass
                
        return gpus

    def get_current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")
