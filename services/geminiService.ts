import { SchemaType } from "@google/generative-ai";
import { AnalysisResult, HardwareProfile } from "../types";
import { analyzeCodeStatic } from "./staticAnalyzer";

// Initialize Gemini Client

// P0-1: Prioritize GEMINI_API_KEY for consistency, fallback to API_KEY
// const apiKey = process.env.GEMINI_API_KEY || process.env.API_KEY;

// if (!apiKey) {
//   console.error("Missing API Key. Please set GEMINI_API_KEY in .env.local");
// }

// const genAI = new GoogleGenerativeAI(apiKey);

// Region Carbon Intensity Map (Duplicated from HardwareSelector to avoid circular deps/React imports)
const REGION_CARBON_INTENSITY: Record<string, number> = {
  'us-central1': 360,
  'asia-east1': 620,
  'europe-west4': 180,
  'global': 450,
  'us-east1': 480
};

// Custom Error Types for better UI handling
export class GeminiError extends Error {
  constructor(message: string, public isRetryable: boolean = false) {
    super(message);
    this.name = "GeminiError";
  }
}

// Retry Logic Helper
async function retryOperation<T>(operation: () => Promise<T>, retries = 1, delay = 2000): Promise<T> {
  try {
    return await operation();
  } catch (error: any) {
    const errorString = JSON.stringify(error);
    const isRateLimit =
      error.status === 429 ||
      error.code === 429 ||
      errorString.includes("429") ||
      errorString.includes("quota") ||
      errorString.includes("RESOURCE_EXHAUSTED");

    if (retries > 0 && (error.status === 503 || isRateLimit || error.message?.includes("fetch"))) {
      await new Promise(res => setTimeout(res, delay));
      return retryOperation(operation, retries - 1, delay * 2);
    }
    throw error;
  }
}

async function processImageForGemini(dataUrl: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.crossOrigin = "Anonymous"; 
    
    img.onload = () => {
      try {
        const canvas = document.createElement('canvas');
        const MAX_WIDTH = 1024;
        const scale = img.width > MAX_WIDTH ? MAX_WIDTH / img.width : 1;
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error("Browser Canvas context failed"));
          return;
        }

        ctx.fillStyle = "#FFFFFF";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        
        const pngDataUrl = canvas.toDataURL("image/png");
        const base64Data = pngDataUrl.split(',')[1];
        resolve(base64Data);
      } catch (e) {
        reject(e);
      }
    };

    img.onerror = (err) => {
      console.error("Image loading error", err);
      reject(new Error("Failed to load or rasterize image."));
    };

    img.src = dataUrl;
  });
}

export const analyzeAndOptimizeStream = async (
  code: string,
  hardware: HardwareProfile,
  onChunk: (text: string) => void,
  imageBase64?: string,
  scope: 'snippet' | 'module' = 'snippet',
  onPhaseChange?: (phase: string) => void
): Promise<AnalysisResult> => {
  onPhaseChange?.('ANALYSIS');
  onChunk('> [System] Connecting to EcoCompute API...\n');
  
  // Step 1: Run Static Analysis (Enhanced P1-1)
  const staticData = analyzeCodeStatic(code);
  const estimatedGFlops = staticData.estimatedFlops;
  const layerSummary = JSON.stringify(staticData.layerCounts);
  
  // Flatten highlights for the prompt
  const structuralHighlights = staticData.structuralHighlights.map(h => h.label).join(", ");

  // Step 2: Prepare Image
  let visionPart = null;
  if (imageBase64) {
    try {
      const pngBase64 = await processImageForGemini(imageBase64);
      visionPart = { 
        inlineData: { 
          mimeType: "image/png", 
          data: pngBase64 
        } 
      };
    } catch (e) {
      console.warn("Vision processing failed:", e);
      onChunk("\n[System Warning: Image processing failed. Proceeding with code analysis only...]\n");
    }
  }

  // Step 3: System Instruction
  // P0-2: Explicit Phase Tags for Real Streaming
  // P0-3: Explainability Requirements & Code Execution Fallback
  const systemInstruction = `
    You are **DeepGreen AI**, an energy optimization agent powered by Gemini 3.
    
    ## TASK SCOPE: ${scope === 'module' ? 'FULL MODULE / PROJECT SCAN' : 'CODE SNIPPET ANALYSIS'}
    Target Hardware: ${hardware.name} (${hardware.type}).
    Target Region: ${hardware.region || 'Global Average'} (Carbon Intensity: ${hardware.carbonIntensity || 'Unknown'} gCO2/kWh).

    ## CRITICAL: REAL-TIME STREAMING PROTOCOL
    You MUST output specific tags on a new line when you start a new phase. 
    Use exactly these tags:
    [[PHASE: SEARCH]] - When using Google Search.
    [[PHASE: COMPUTE]] - When running Python code to verify math.
    [[PHASE: ANALYSIS]] - When analyzing bottlenecks.
    [[PHASE: STRATEGY]] - When formulating the final Green AI strategy.

    ## GROUNDING DATA (Static Analysis)
    - **Valid Python Syntax**: ${staticData.isValid}
    - **Detected Layers**: ${layerSummary}
    - **Structural Highlights**: ${structuralHighlights}
    - **Estimated Compute**: ${estimatedGFlops} GFLOPs (theoretical - use as baseline)

    ## MANDATORY TOOL USE & FALLBACKS
    1. **GOOGLE SEARCH**: 
       - Find **2026 hardware specifications** for '${hardware.name}'. Look for TDP and Joules/Op.
       - **FINOPS CHECK**: Search for "On-demand price per hour for ${hardware.name} on AWS/GCP/Azure".
       - **MLPerf Validation**: Search for "MLPerf Inference v4.0" or "v5.0" results for this hardware class.
    
    2. **CODE EXECUTION (Calculus)**: 
       - Calculate Arithmetic Intensity (FLOPs / Byte) using Python.
       - Verify tensor shape compatibility.
    
    3. **CARBON CALCULATOR**:
       - Use the 'calculate_carbon_footprint' tool to get precise emissions based on energy usage and region.
    
    **FALLBACK**: If Code Execution fails, state in 'assumptions' that values are 'Estimated via Static Analysis'.

    ## EXPLAINABILITY REQUIREMENT
    You must populate 'assumptions', 'citations', and 'energy_model' in the JSON output. 
    Do not make up numbers. State your sources.

    ## CRITICAL BUG DETECTION
    If the user's code implies a specific architecture (like ResNet, Transformer) but is **missing key components** (e.g., missing residual connection 'x + out', missing LayerNorm, missing activation), you MUST start the 'bottleneckAnalysis' field with the exact text: "CRITICAL BUG:".

    ## OUTPUT SCHEMA
    Return JSON strictly matching the schema.
  `;

  const textPrompt = visionPart 
    ? `Analyze the attached neural network sketch/diagram for ${hardware.name}. \n\nINSTRUCTION: Use the visual diagram as the PRIMARY source for the architecture. The code below is context. \n\nCode Context:\n${code}`
    : `Analyze this PyTorch code for ${hardware.name} (ID: ${hardware.id}):\n${code}`;

  const parts: any[] = [{ text: textPrompt }];
  if (visionPart) {
    parts.unshift(visionPart);
  }

  return retryOperation(async () => {
    try {
      const region = hardware.region || 'global';
      const intensity = REGION_CARBON_INTENSITY[region] || REGION_CARBON_INTENSITY['global'] || 450;
      onChunk(`> [System] Static analysis: ~${estimatedGFlops} GFLOPs, Layers=${layerSummary}, Region=${region} (${intensity}g/kWh)\n`);
      onPhaseChange?.('STRATEGY');
      onChunk('> [System] Requesting optimization from server...\n');

      const resp = await fetch('/api/gemini', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          code,
          hardware,
          scope,
          imagePngBase64: visionPart?.inlineData?.data || undefined,
        }),
      });

      if (!resp.ok) {
        const txt = await resp.text();
        throw new GeminiError(txt || `Request failed (${resp.status})`, resp.status >= 500);
      }

      const data = (await resp.json()) as AnalysisResult;
      onChunk('> [System] Optimization response received.\n');
      return data;
    } catch (error: any) {
      console.error('Gemini Failure:', error);

      const rawMsg = typeof error?.message === 'string' ? error.message : String(error);
      const status = error?.status ?? error?.code;

      if (
        status === 429 ||
        rawMsg.includes('429') ||
        rawMsg.toLowerCase().includes('quota') ||
        rawMsg.includes('RESOURCE_EXHAUSTED')
      ) {
        throw new GeminiError(
          'Gemini Quota Exceeded (429). Please wait a moment or try again later.',
          true
        );
      }

      if (error instanceof GeminiError) throw error;
      throw new GeminiError(rawMsg || 'Unknown API Error', true);
    }
  });
};