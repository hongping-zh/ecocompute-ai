"""
Tests for EcoCompute AI auditor module.
"""

import unittest
import time
from unittest.mock import patch, MagicMock


class TestEnergyAuditor(unittest.TestCase):
    """Tests for EnergyAuditor class."""
    
    @patch('ecocompute.auditor.NVML_AVAILABLE', True)
    @patch('ecocompute.auditor.pynvml')
    def test_auditor_initialization(self, mock_pynvml):
        """Test auditor initializes correctly."""
        from ecocompute import EnergyAuditor
        
        auditor = EnergyAuditor(gpu_index=0, sample_interval_ms=100)
        
        self.assertEqual(auditor.gpu_index, 0)
        self.assertEqual(auditor.sample_interval_ms, 100)
        self.assertFalse(auditor._running)
    
    @patch('ecocompute.auditor.NVML_AVAILABLE', True)
    @patch('ecocompute.auditor.pynvml')
    def test_auditor_start_stop(self, mock_pynvml):
        """Test auditor start and stop."""
        from ecocompute import EnergyAuditor
        
        # Mock NVML functions
        mock_pynvml.nvmlDeviceGetPowerUsage.return_value = 200000  # 200W in mW
        
        auditor = EnergyAuditor(gpu_index=0, sample_interval_ms=50)
        auditor.start()
        
        self.assertTrue(auditor._running)
        
        # Let it sample a few times
        time.sleep(0.2)
        
        energy, avg_power, peak_power = auditor.stop()
        
        self.assertFalse(auditor._running)
        self.assertGreaterEqual(energy, 0)
        self.assertGreaterEqual(avg_power, 0)
        self.assertGreaterEqual(peak_power, 0)
    
    @patch('ecocompute.auditor.NVML_AVAILABLE', True)
    @patch('ecocompute.auditor.pynvml')
    def test_auditor_double_start_raises(self, mock_pynvml):
        """Test that starting twice raises an error."""
        from ecocompute import EnergyAuditor
        
        auditor = EnergyAuditor(gpu_index=0)
        auditor.start()
        
        with self.assertRaises(RuntimeError):
            auditor.start()
        
        auditor.stop()
    
    @patch('ecocompute.auditor.NVML_AVAILABLE', True)
    @patch('ecocompute.auditor.pynvml')
    def test_auditor_stop_without_start_raises(self, mock_pynvml):
        """Test that stopping without starting raises an error."""
        from ecocompute import EnergyAuditor
        
        auditor = EnergyAuditor(gpu_index=0)
        
        with self.assertRaises(RuntimeError):
            auditor.stop()


class TestUtils(unittest.TestCase):
    """Tests for utility functions."""
    
    def test_calculate_carbon_footprint(self):
        """Test carbon footprint calculation."""
        from ecocompute.utils import calculate_carbon_footprint
        
        # 1 kWh = 3,600,000 J
        result = calculate_carbon_footprint(3600000, region="us-east")
        
        self.assertEqual(result["energy_kwh"], 1.0)
        self.assertEqual(result["carbon_g"], 400.0)  # 400 gCO2/kWh for us-east
        self.assertEqual(result["carbon_kg"], 0.4)
    
    def test_calculate_carbon_footprint_custom_intensity(self):
        """Test carbon footprint with custom intensity."""
        from ecocompute.utils import calculate_carbon_footprint
        
        result = calculate_carbon_footprint(3600000, custom_intensity=100)
        
        self.assertEqual(result["carbon_g"], 100.0)
    
    def test_estimate_training_cost(self):
        """Test training cost estimation."""
        from ecocompute.utils import estimate_training_cost
        
        result = estimate_training_cost(
            model_params=1.3e9,
            training_tokens=100e9,
            gpu_type="A100-80GB",
            num_gpus=8,
        )
        
        self.assertIn("cost_usd", result)
        self.assertIn("training_days", result)
        self.assertIn("carbon_kg", result)
        self.assertGreater(result["cost_usd"], 0)
        self.assertGreater(result["training_days"], 0)
    
    def test_format_training_estimate(self):
        """Test training estimate formatting."""
        from ecocompute.utils import estimate_training_cost, format_training_estimate
        
        estimate = estimate_training_cost(
            model_params=1.3e9,
            training_tokens=100e9,
        )
        
        formatted = format_training_estimate(estimate)
        
        self.assertIn("1.3B", formatted)
        self.assertIn("days", formatted)
        self.assertIn("$", formatted)


class TestCarbonIntensity(unittest.TestCase):
    """Tests for carbon intensity data."""
    
    def test_region_carbon_intensity_values(self):
        """Test that all regions have valid carbon intensity values."""
        from ecocompute.utils import REGION_CARBON_INTENSITY
        
        for region, intensity in REGION_CARBON_INTENSITY.items():
            self.assertIsInstance(intensity, (int, float))
            self.assertGreater(intensity, 0)
            self.assertLess(intensity, 1000)  # Sanity check
    
    def test_eu_north_is_cleanest(self):
        """Test that EU North (Nordic) has lowest carbon intensity."""
        from ecocompute.utils import REGION_CARBON_INTENSITY
        
        eu_north = REGION_CARBON_INTENSITY["eu-north"]
        
        for region, intensity in REGION_CARBON_INTENSITY.items():
            if region != "eu-north":
                self.assertLessEqual(eu_north, intensity)


class TestGPUSpecs(unittest.TestCase):
    """Tests for GPU specifications data."""
    
    def test_gpu_specs_completeness(self):
        """Test that all GPUs have required specs."""
        from ecocompute.utils import GPU_SPECS
        
        required_keys = ["tdp", "tflops_fp16", "memory_gb"]
        
        for gpu, specs in GPU_SPECS.items():
            for key in required_keys:
                self.assertIn(key, specs, f"GPU {gpu} missing {key}")
    
    def test_rtx5090_specs(self):
        """Test RTX 5090 specifications."""
        from ecocompute.utils import GPU_SPECS
        
        rtx5090 = GPU_SPECS["RTX-5090"]
        
        self.assertEqual(rtx5090["tdp"], 575)
        self.assertEqual(rtx5090["memory_gb"], 32)


if __name__ == "__main__":
    unittest.main()
