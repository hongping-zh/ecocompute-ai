"""
EcoCompute AI - High-Fidelity Energy-Economic Auditor for Large-Scale AI Training

A framework for energy auditing and cost estimation of LLM development.
"""

from .auditor import EnergyAuditor
from .hf_callback import EcoComputeCallback
from .utils import calculate_carbon_footprint, estimate_training_cost

__version__ = "1.0.0"
__author__ = "Hongping Zhang"
__all__ = [
    "EnergyAuditor",
    "EcoComputeCallback", 
    "calculate_carbon_footprint",
    "estimate_training_cost",
]
