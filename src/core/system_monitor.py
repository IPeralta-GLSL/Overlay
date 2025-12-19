import psutil
import datetime
import subprocess
import shutil
import platform
import time
import os
import sys

class SystemMonitor:
    def __init__(self):
        self._cpu_name_cache = None
        self._gpu_info_cache = None
        self._gpu_cache_time = 0
        self._gpu_cache_duration = 5
        self._lhm_computer = None
        self._lhm_initialized = False
        self._Hardware = None
        self._init_lhm()

    def _init_lhm(self):
        if platform.system() != "Windows":
            return
        try:
            if getattr(sys, 'frozen', False):
                base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
            else:
                base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            dll_path = os.path.join(base_path, "lib", "LibreHardwareMonitorLib.dll")
            if not os.path.exists(dll_path):
                self._lhm_initialized = False
                return
            
            from clr_loader import get_coreclr, get_netfx
            from pythonnet import set_runtime
            
            try:
                runtime = get_netfx()
                set_runtime(runtime)
            except Exception:
                try:
                    runtime = get_coreclr()
                    set_runtime(runtime)
                except Exception:
                    pass
            
            import clr
            clr.AddReference(dll_path)
            from LibreHardwareMonitor import Hardware
            self._Hardware = Hardware
            self._lhm_computer = Hardware.Computer()
            self._lhm_computer.IsCpuEnabled = True
            self._lhm_computer.IsGpuEnabled = True
            self._lhm_computer.IsMemoryEnabled = True
            self._lhm_computer.Open()
            self._lhm_initialized = True
        except Exception as e:
            self._lhm_initialized = False
            self._init_error = str(e)

    def _update_hardware(self):
        if self._lhm_computer:
            for hw in self._lhm_computer.Hardware:
                hw.Update()
                for sub in hw.SubHardware:
                    sub.Update()

    @property
    def cpu_name(self):
        if self._cpu_name_cache is None:
            self._cpu_name_cache = self._get_cpu_name()
        return self._cpu_name_cache

    def _get_cpu_name(self):
        if self._lhm_initialized and self._lhm_computer:
            for hw in self._lhm_computer.Hardware:
                if hw.HardwareType == self._Hardware.HardwareType.Cpu:
                    return hw.Name
        try:
            if platform.system() == "Windows":
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
                cpu_name, _ = winreg.QueryValueEx(key, "ProcessorNameString")
                winreg.CloseKey(key)
                return cpu_name.strip()
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
        if self._lhm_initialized and self._lhm_computer:
            self._update_hardware()
            for hw in self._lhm_computer.Hardware:
                if hw.HardwareType == self._Hardware.HardwareType.Cpu:
                    for sensor in hw.Sensors:
                        if sensor.SensorType == self._Hardware.SensorType.Load and "Total" in sensor.Name:
                            if sensor.Value is not None:
                                return float(sensor.Value)
        return psutil.cpu_percent(interval=None)

    def get_ram_usage(self):
        if self._lhm_initialized and self._lhm_computer:
            self._update_hardware()
            for hw in self._lhm_computer.Hardware:
                if hw.HardwareType == self._Hardware.HardwareType.Memory:
                    for sensor in hw.Sensors:
                        if sensor.SensorType == self._Hardware.SensorType.Load and "Memory" in sensor.Name:
                            if sensor.Value is not None:
                                return float(sensor.Value)
        return psutil.virtual_memory().percent

    def get_cpu_temperature(self):
        if self._lhm_initialized and self._lhm_computer:
            self._update_hardware()
            for hw in self._lhm_computer.Hardware:
                if hw.HardwareType == self._Hardware.HardwareType.Cpu:
                    for sensor in hw.Sensors:
                        if sensor.SensorType == self._Hardware.SensorType.Temperature:
                            if sensor.Value is not None and sensor.Value > 0:
                                return float(sensor.Value)
        if platform.system() == "Linux":
            try:
                temps = psutil.sensors_temperatures()
                if temps:
                    for name in ["coretemp", "k10temp", "zenpower", "cpu_thermal", "acpitz"]:
                        if name in temps:
                            return temps[name][0].current
                    first_sensor = list(temps.values())[0]
                    if first_sensor:
                        return first_sensor[0].current
            except:
                pass
        return None

    def get_gpu_temperature(self):
        temps = []
        if self._lhm_initialized and self._lhm_computer:
            self._update_hardware()
            for hw in self._lhm_computer.Hardware:
                if hw.HardwareType in [self._Hardware.HardwareType.GpuNvidia, 
                                        self._Hardware.HardwareType.GpuAmd,
                                        self._Hardware.HardwareType.GpuIntel]:
                    for sensor in hw.Sensors:
                        if sensor.SensorType == self._Hardware.SensorType.Temperature:
                            if sensor.Value is not None and sensor.Value > 0:
                                temps.append(float(sensor.Value))
                                break
            if temps:
                return temps
        if platform.system() == "Linux":
            try:
                sensor_temps = psutil.sensors_temperatures()
                for name in ["amdgpu", "radeon", "nouveau"]:
                    if name in sensor_temps:
                        temps.append(sensor_temps[name][0].current)
            except:
                pass
        if shutil.which("nvidia-smi"):
            try:
                output = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
                    creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
                ).decode("utf-8").strip().split('\n')
                for temp in output:
                    temps.append(float(temp.strip()))
            except:
                pass
        return temps if temps else None

    def get_gpu_info(self):
        current_time = time.time()
        if self._gpu_info_cache and (current_time - self._gpu_cache_time) < self._gpu_cache_duration:
            return self._get_gpu_usage_from_cache()

        gpus = []
        if self._lhm_initialized and self._lhm_computer:
            self._update_hardware()
            for hw in self._lhm_computer.Hardware:
                if hw.HardwareType in [self._Hardware.HardwareType.GpuNvidia,
                                        self._Hardware.HardwareType.GpuAmd,
                                        self._Hardware.HardwareType.GpuIntel]:
                    gpu_type = "nvidia" if hw.HardwareType == self._Hardware.HardwareType.GpuNvidia else \
                               "amd" if hw.HardwareType == self._Hardware.HardwareType.GpuAmd else "intel"
                    usage = 0.0
                    for sensor in hw.Sensors:
                        if sensor.SensorType == self._Hardware.SensorType.Load and "Core" in sensor.Name:
                            if sensor.Value is not None:
                                usage = float(sensor.Value)
                                break
                    gpus.append({"name": hw.Name, "type": gpu_type, "usage": usage})

        if not gpus:
            gpus = self._get_gpu_info_fallback()

        self._gpu_info_cache = gpus
        self._gpu_cache_time = current_time

        return [(g["name"], g.get("usage", 0.0)) for g in gpus]

    def _get_gpu_usage_from_cache(self):
        if self._lhm_initialized and self._lhm_computer:
            self._update_hardware()
            result = []
            for hw in self._lhm_computer.Hardware:
                if hw.HardwareType in [self._Hardware.HardwareType.GpuNvidia,
                                        self._Hardware.HardwareType.GpuAmd,
                                        self._Hardware.HardwareType.GpuIntel]:
                    usage = 0.0
                    for sensor in hw.Sensors:
                        if sensor.SensorType == self._Hardware.SensorType.Load and "Core" in sensor.Name:
                            if sensor.Value is not None:
                                usage = float(sensor.Value)
                                break
                    result.append((hw.Name, usage))
            if result:
                return result
        return [(g["name"], g.get("usage", 0.0)) for g in self._gpu_info_cache]

    def _get_gpu_info_fallback(self):
        gpus = []
        if shutil.which("nvidia-smi"):
            try:
                kwargs = {"creationflags": subprocess.CREATE_NO_WINDOW} if platform.system() == "Windows" else {}
                names = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
                    **kwargs
                ).decode("utf-8").strip().split('\n')
                usages = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
                    **kwargs
                ).decode("utf-8").strip().split('\n')
                for i, name in enumerate(names):
                    usage = float(usages[i].strip()) if i < len(usages) else 0.0
                    gpus.append({"name": name.strip(), "type": "nvidia", "usage": usage})
            except:
                pass

        if platform.system() == "Windows" and not gpus:
            try:
                command = ["powershell", "-Command", "Get-CimInstance -ClassName Win32_VideoController | Select-Object -ExpandProperty Name"]
                output = subprocess.check_output(
                    command,
                    creationflags=subprocess.CREATE_NO_WINDOW
                ).decode().strip()
                lines = output.split("\n")
                for line in lines:
                    if line.strip():
                        name = line.strip()
                        gpu_type = "amd" if "AMD" in name or "ATI" in name else "nvidia" if "NVIDIA" in name else "intel" if "Intel" in name else "other"
                        gpus.append({"name": name, "type": gpu_type, "usage": 0.0})
            except:
                pass

        return gpus

    def get_current_time(self):
        return datetime.datetime.now().strftime("%H:%M:%S")

    def clear_cache(self):
        self._cpu_name_cache = None
        self._gpu_info_cache = None
        self._gpu_cache_time = 0

    def close(self):
        if self._lhm_computer:
            try:
                self._lhm_computer.Close()
            except:
                pass
            self._lhm_computer = None
            self._lhm_initialized = False
