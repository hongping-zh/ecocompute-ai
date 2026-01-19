
export interface HardwareProfile {
  id: string;
  name: string;
  type: 'GPU' | 'TPU' | 'CPU' | 'Mobile';
  icon: string;
  efficiency: string; // e.g. "Low", "Medium", "High"
  region?: string; // e.g., "us-central1"
  carbonIntensity?: number; // gCO2/kWh
}

export interface EnergyBreakdownItem {
  component: string;
  percentage: number;
  joules: number;
  color: string;
  [key: string]: any;
}

export interface RecommendationItem {
  title: string;
  gain: string; // e.g. "15-20%"
  reasoning: string;
  category: 'High' | 'Medium' | 'Exploratory';
}

export interface TradeoffMetrics {
  performanceScore: number; // 0-100 (Higher is faster)
  costEfficiencyScore: number; // 0-100 (Higher is cheaper)
  carbonEfficiencyScore: number; // 0-100 (Higher is greener)
}

export interface BenchmarkData {
  found: boolean;
  source: string; // e.g., "MLPerf Inference v4.0"
  device: string; // e.g., "NVIDIA H100"
  metric: string; // e.g., "Joules/Stream"
  value: string; // e.g., "450 J"
}

export interface AnalysisResult {
  // Quantitative Metrics
  originalEnergyJoules: number;
  optimizedEnergyJoules: number;
  improvementPercentage: number;
  carbonSavedGrams: number;
  
  estimatedHourlyCost?: number;
  costSavingsPer1MInference?: number;
  
  // Uncertainty Quantification
  confidenceScore: number; // 0.0 to 1.0
  uncertaintyFactors: string[]; // List of factors lowering confidence
  strategyAnalysis: string; // Strategic advice based on confidence level
  
  // Decision Support
  tradeoffMetrics: TradeoffMetrics; // New: Triangle Model Data

  // Transparency & Explainability (P0-3)
  assumptions: string[]; // e.g., "Batch Size = 1", "FP16 Precision"
  citations: string[]; // e.g., "NVIDIA B200 Datasheet (2025)"
  energy_model: string; // Explanation of how GFLOPs -> Joules was derived

  // MLPerf Validation
  benchmarkData?: BenchmarkData;

  // Qualitative Analysis
  reasoning_trace: string; // Explicit Chain of Thought
  bottleneckAnalysis: string;
  impactAnalogy: string;
  
  // Categorized Recommendations
  recommendations: RecommendationItem[];
  
  // Code & Charts
  optimizedCode: string;
  breakdown: EnergyBreakdownItem[];
}
