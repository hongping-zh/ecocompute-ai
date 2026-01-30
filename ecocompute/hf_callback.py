"""
Hugging Face Integration - TrainerCallback for real-time energy logging.
"""

import time
from typing import Optional, Dict, Any

try:
    from transformers import TrainerCallback, TrainerState, TrainerControl, TrainingArguments
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    TrainerCallback = object

from .auditor import EnergyAuditor, NVML_AVAILABLE


class EcoComputeCallback(TrainerCallback):
    """
    Hugging Face TrainerCallback for real-time energy logging during training.
    
    Automatically tracks energy consumption per epoch and logs metrics.
    
    Example:
        >>> from transformers import Trainer
        >>> from ecocompute import EcoComputeCallback
        >>> 
        >>> callback = EcoComputeCallback(gpu_index=0, log_to_wandb=True)
        >>> trainer = Trainer(
        ...     model=model,
        ...     args=training_args,
        ...     callbacks=[callback],
        ... )
        >>> trainer.train()
    """
    
    def __init__(
        self,
        gpu_index: int = 0,
        sample_interval_ms: int = 100,
        log_to_wandb: bool = False,
        carbon_intensity_gco2_kwh: float = 400.0,
    ):
        """
        Initialize the EcoCompute callback.
        
        Args:
            gpu_index: Index of the GPU to monitor
            sample_interval_ms: Power sampling interval in milliseconds
            log_to_wandb: Whether to log metrics to Weights & Biases
            carbon_intensity_gco2_kwh: Regional carbon intensity (gCO2/kWh)
        """
        if not HF_AVAILABLE:
            raise ImportError(
                "transformers is required for EcoComputeCallback. "
                "Install it with: pip install transformers"
            )
        
        if not NVML_AVAILABLE:
            raise ImportError(
                "pynvml is required for EcoComputeCallback. "
                "Install it with: pip install pynvml"
            )
        
        self.gpu_index = gpu_index
        self.sample_interval_ms = sample_interval_ms
        self.log_to_wandb = log_to_wandb
        self.carbon_intensity = carbon_intensity_gco2_kwh
        
        self._auditor: Optional[EnergyAuditor] = None
        self._epoch_start_time: float = 0.0
        self._total_energy: float = 0.0
        self._total_carbon: float = 0.0
        self._epoch_metrics: list = []
        
    def on_train_begin(self, args: "TrainingArguments", state: "TrainerState", 
                       control: "TrainerControl", **kwargs):
        """Called at the beginning of training."""
        self._total_energy = 0.0
        self._total_carbon = 0.0
        self._epoch_metrics = []
        print(f"[EcoCompute] Starting energy monitoring on GPU {self.gpu_index}")
        
    def on_epoch_begin(self, args: "TrainingArguments", state: "TrainerState",
                       control: "TrainerControl", **kwargs):
        """Called at the beginning of each epoch."""
        self._auditor = EnergyAuditor(self.gpu_index, self.sample_interval_ms)
        self._auditor.start()
        self._epoch_start_time = time.time()
        
    def on_epoch_end(self, args: "TrainingArguments", state: "TrainerState",
                     control: "TrainerControl", **kwargs):
        """Called at the end of each epoch."""
        if self._auditor is None:
            return
        
        energy, avg_power, peak_power = self._auditor.stop()
        epoch_time = time.time() - self._epoch_start_time
        
        # Calculate carbon footprint
        energy_kwh = energy / 3600000  # J to kWh
        carbon_g = energy_kwh * self.carbon_intensity
        
        self._total_energy += energy
        self._total_carbon += carbon_g
        
        metrics = {
            "epoch": state.epoch,
            "energy_j": energy,
            "avg_power_w": avg_power,
            "peak_power_w": peak_power,
            "epoch_time_s": epoch_time,
            "carbon_g": carbon_g,
        }
        self._epoch_metrics.append(metrics)
        
        print(f"[EcoCompute] Epoch {state.epoch:.0f}: "
              f"Energy={energy:.1f}J, Avg Power={avg_power:.1f}W, "
              f"Carbon={carbon_g:.2f}g CO2e")
        
        # Log to W&B if enabled
        if self.log_to_wandb:
            try:
                import wandb
                wandb.log({
                    "ecocompute/energy_j": energy,
                    "ecocompute/avg_power_w": avg_power,
                    "ecocompute/peak_power_w": peak_power,
                    "ecocompute/carbon_g": carbon_g,
                })
            except ImportError:
                pass
        
        self._auditor = None
        
    def on_train_end(self, args: "TrainingArguments", state: "TrainerState",
                     control: "TrainerControl", **kwargs):
        """Called at the end of training."""
        print(f"\n[EcoCompute] Training Complete")
        print(f"  Total Energy: {self._total_energy:.1f} J ({self._total_energy/3600:.2f} Wh)")
        print(f"  Total Carbon: {self._total_carbon:.2f} g CO2e")
        
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of energy metrics.
        
        Returns:
            Dictionary with total energy, carbon, and per-epoch metrics
        """
        return {
            "total_energy_j": self._total_energy,
            "total_energy_wh": self._total_energy / 3600,
            "total_carbon_g": self._total_carbon,
            "carbon_intensity_gco2_kwh": self.carbon_intensity,
            "epoch_metrics": self._epoch_metrics,
        }
