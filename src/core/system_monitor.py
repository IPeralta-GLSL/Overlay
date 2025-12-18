import psutil
import datetime
import subprocess
import shutil
import platform
import time

class SystemMonitor:
    def __init__(self):
        self._cpu_name_cache = None
        self._gpu_info_cache = None
        self._gpu_cache_time = 0
        self._gpu_cache_duration = 60

    @property
    def cpu_name(self):
        if self._cpu_name_cache is None:
            self._cpu_name_cache = self._get_cpu_name()
        return self._cpu_name_cache

    def _get_cpu_name(self):
        try:
            if platform.system() == "Windows":
                command = "wmic cpu get name"
                output = subprocess.check_output(
                    command, shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode().strip()
                return output.split("\n")[1].strip()
            elif platform.system() == "Linux":
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
                return platform.processor()
            else:
                return platform.processor()
        except:
            return "CPU"

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=None)

    def get_ram_usage(self):
        return psutil.virtual_memory().percent

    def get_cpu_temperature(self):
        try:
            if platform.system() == "Linux":
                temps = psutil.sensors_temperatures()
                if temps:
                    for name in ["coretemp", "k10temp", "zenpower", "cpu_thermal", "acpitz"]:
                        if name in temps:
                            return temps[name][0].current
                    first_sensor = list(temps.values())[0]
                    if first_sensor:
                        return first_sensor[0].current
            elif platform.system() == "Windows":
                try:
                    import wmi
                    w = wmi.WMI(namespace="root\\wmi")
                    temp_info = w.MSAcpi_ThermalZoneTemperature()[0]
                    return (temp_info.CurrentTemperature / 10.0) - 273.15
                except:
                    pass
        except:
            pass
        return None

    def get_gpu_temperature(self):
        temps = []
        if shutil.which("nvidia-smi"):
            try:
                kwargs = {}
                if platform.system() == "Windows":
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                output = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                    **kwargs
                ).decode("utf-8").strip().split('\n')
                for temp in output:
                    temps.append(float(temp.strip()))
            except:
                pass

        if not temps and shutil.which("rocm-smi"):
            try:
                kwargs = {}
                if platform.system() == "Windows":
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                output = subprocess.check_output(
                    ["rocm-smi", "--showtemp"],
                    **kwargs
                ).decode("utf-8")
                seen_gpus = set()
                for line in output.split('\n'):
                    if "edge" in line.lower():
                        parts = line.split()
                        gpu_id = None
                        for part in parts:
                            if part.startswith("GPU["):
                                gpu_id = part
                                break
                        if gpu_id and gpu_id not in seen_gpus:
                            for part in parts:
                                try:
                                    temp = float(part.replace('c', '').replace('C', ''))
                                    if 0 < temp < 150:
                                        temps.append(temp)
                                        seen_gpus.add(gpu_id)
                                        break
                                except:
                                    continue
            except:
                pass

        if not temps and platform.system() == "Linux":
            try:
                sensor_temps = psutil.sensors_temperatures()
                for name in ["amdgpu", "radeon", "nouveau"]:
                    if name in sensor_temps:
                        temps.append(sensor_temps[name][0].current)
            except:
                pass

        return temps if temps else None

    def get_gpu_info(self):
        current_time = time.time()
        if self._gpu_info_cache and (current_time - self._gpu_cache_time) < self._gpu_cache_duration:
            return self._update_gpu_usage(self._gpu_info_cache)

        gpus = []

        if shutil.which("nvidia-smi"):
            try:
                kwargs = {}
                if platform.system() == "Windows":
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                names = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    **kwargs
                ).decode("utf-8").strip().split('\n')
                for name in names:
                    gpus.append({"name": name.strip(), "type": "nvidia"})
            except:
                pass

        if shutil.which("rocm-smi"):
            try:
                kwargs = {}
                if platform.system() == "Windows":
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                output = subprocess.check_output(
                    ["rocm-smi", "--showproductname"],
                    **kwargs
                ).decode("utf-8")
                seen_gpus = set()
                for line in output.split('\n'):
                    if "Card Series:" in line:
                        parts = line.split(":")
                        if len(parts) >= 3:
                            gpu_id = parts[0].strip()
                            if gpu_id not in seen_gpus:
                                gpu_name = parts[2].strip()
                                gpus.append({"name": gpu_name, "type": "amd"})
                                seen_gpus.add(gpu_id)
            except:
                pass

        if not gpus and platform.system() == "Linux":
            try:
                output = subprocess.check_output(
                    ["lspci"],
                    stderr=subprocess.DEVNULL
                ).decode("utf-8")
                for line in output.split('\n'):
                    if "VGA" in line or "3D" in line:
                        parts = line.split(":")
                        if len(parts) > 2:
                            name = parts[2].strip()
                            gpu_type = "amd" if "AMD" in name or "ATI" in name else "nvidia" if "NVIDIA" in name else "other"
                            gpus.append({"name": name, "type": gpu_type})
            except:
                pass

        if not gpus and platform.system() == "Windows":
            try:
                command = "wmic path win32_VideoController get name"
                output = subprocess.check_output(
                    command, shell=True,
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode().strip()
                lines = output.split("\n")[1:]
                for line in lines:
                    if line.strip():
                        name = line.strip()
                        gpu_type = "amd" if "AMD" in name or "ATI" in name else "nvidia" if "NVIDIA" in name else "other"
                        gpus.append({"name": name, "type": gpu_type})
            except:
                pass

        self._gpu_info_cache = gpus
        self._gpu_cache_time = current_time

        return self._update_gpu_usage(gpus)

    def _update_gpu_usage(self, gpus):
        result = []
        nvidia_usages = []
        amd_usages = []

        if shutil.which("nvidia-smi"):
            try:
                kwargs = {}
                if platform.system() == "Windows":
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                output = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                    **kwargs
                ).decode("utf-8").strip().split('\n')
                nvidia_usages = [float(u.strip()) for u in output]
            except:
                pass

        if shutil.which("rocm-smi"):
            try:
                kwargs = {}
                if platform.system() == "Windows":
                    kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                output = subprocess.check_output(
                    ["rocm-smi", "--showuse"],
                    **kwargs
                ).decode("utf-8")
                for line in output.split('\n'):
                    if "GPU use (%)" in line:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            try:
                                usage = float(parts[-1].strip())
                                amd_usages.append(usage)
                            except:
                                pass
            except:
                pass

        nvidia_idx = 0
        amd_idx = 0
        for gpu in gpus:
            if gpu["type"] == "nvidia" and nvidia_idx < len(nvidia_usages):
                result.append((gpu["name"], nvidia_usages[nvidia_idx]))
                nvidia_idx += 1
            elif gpu["type"] == "amd" and amd_idx < len(amd_usages):
                result.append((gpu["name"], amd_usages[amd_idx]))
                amd_idx += 1
            else:
                result.append((gpu["name"], 0.0))

        return result

    def get_current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def clear_cache(self):
        self._cpu_name_cache = None
        self._gpu_info_cache = None
        self._gpu_cache_time = 0
