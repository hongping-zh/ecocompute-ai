"""
EcoCore Auditor - High-frequency power sampling via NVML integration.
"""

import time
import threading
from typing import Optional, Tuple, List

try:
    import pynvml
    NVML_AVAILABLE = True
except ImportError:
    NVML_AVAILABLE = False


class EnergyAuditor:
    """
    High-fidelity energy auditor for GPU workloads.
    
    Uses NVIDIA NVML for real-time power sampling at configurable intervals.
    
    Example:
        >>> auditor = EnergyAuditor(gpu_index=0, sample_interval_ms=100)
        >>> auditor.start()
        >>> # Your inference or training code
        >>> outputs = model.generate(inputs, max_new_tokens=256)
        >>> energy, avg_power, peak_power = auditor.stop()
        >>> print(f"Energy: {energy:.2f} J, Avg Power: {avg_power:.2f} W")
    """
    
    def __init__(self, gpu_index: int = 0, sample_interval_ms: int = 100):
        """
        Initialize the energy auditor.
        
        Args:
            gpu_index: Index of the GPU to monitor (default: 0)
            sample_interval_ms: Power sampling interval in milliseconds (default: 100)
        """
        if not NVML_AVAILABLE:
            raise ImportError(
                "pynvml is required for EnergyAuditor. "
                "Install it with: pip install pynvml"
            )
        
        self.gpu_index = gpu_index
        self.sample_interval_ms = sample_interval_ms
        self.sample_interval_sec = sample_interval_ms / 1000.0
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._power_samples: List[float] = []
        self._timestamps: List[float] = []
        self._handle = None
        
    def start(self) -> None:
        """Start energy monitoring."""
        if self._running:
            raise RuntimeError("Auditor is already running")
        
        pynvml.nvmlInit()
        self._handle = pynvml.nvmlDeviceGetHandleByIndex(self.gpu_index)
        
        self._power_samples = []
        self._timestamps = []
        self._running = True
        
        self._thread = threading.Thread(target=self._sample_loop, daemon=True)
        self._thread.start()
        
    def _sample_loop(self) -> None:
        """Internal sampling loop running in background thread."""
        while self._running:
            try:
                power_mw = pynvml.nvmlDeviceGetPowerUsage(self._handle)
                power_w = power_mw / 1000.0
                
                self._power_samples.append(power_w)
                self._timestamps.append(time.time())
            except pynvml.NVMLError:
                pass
            
            time.sleep(self.sample_interval_sec)
    
    def stop(self) -> Tuple[float, float, float]:
        """
        Stop energy monitoring and return metrics.
        
        Returns:
            Tuple of (total_energy_joules, avg_power_watts, peak_power_watts)
        """
        if not self._running:
            raise RuntimeError("Auditor is not running")
        
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        
        pynvml.nvmlShutdown()
        
        if len(self._power_samples) < 2:
            return 0.0, 0.0, 0.0
        
        # Calculate energy using trapezoidal integration
        total_energy = 0.0
        for i in range(1, len(self._power_samples)):
            dt = self._timestamps[i] - self._timestamps[i-1]
            avg_power = (self._power_samples[i] + self._power_samples[i-1]) / 2
            total_energy += avg_power * dt
        
        avg_power = sum(self._power_samples) / len(self._power_samples)
        peak_power = max(self._power_samples)
        
        return total_energy, avg_power, peak_power
    
    def get_samples(self) -> Tuple[List[float], List[float]]:
        """
        Get raw power samples and timestamps.
        
        Returns:
            Tuple of (power_samples_watts, timestamps)
        """
        return self._power_samples.copy(), self._timestamps.copy()
    
    @staticmethod
    def get_gpu_info(gpu_index: int = 0) -> dict:
        """
        Get GPU information.
        
        Args:
            gpu_index: Index of the GPU
            
        Returns:
            Dictionary with GPU name, memory, and other info
        """
        if not NVML_AVAILABLE:
            return {"error": "pynvml not available"}
        
        pynvml.nvmlInit()
        handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
        
        info = {
            "name": pynvml.nvmlDeviceGetName(handle),
            "memory_total_gb": pynvml.nvmlDeviceGetMemoryInfo(handle).total / (1024**3),
            "power_limit_w": pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000,
        }
        
        pynvml.nvmlShutdown()
        return info


class EnergyAuditorContext:
    """
    Context manager for energy auditing.
    
    Example:
        >>> with EnergyAuditorContext(gpu_index=0) as auditor:
        ...     outputs = model.generate(inputs)
        >>> print(f"Energy: {auditor.energy:.2f} J")
    """
    
    def __init__(self, gpu_index: int = 0, sample_interval_ms: int = 100):
        self.auditor = EnergyAuditor(gpu_index, sample_interval_ms)
        self.energy = 0.0
        self.avg_power = 0.0
        self.peak_power = 0.0
        
    def __enter__(self):
        self.auditor.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.energy, self.avg_power, self.peak_power = self.auditor.stop()
        return False
