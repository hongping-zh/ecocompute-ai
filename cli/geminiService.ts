
import { GoogleGenAI, Type, Tool } from "@google/genai";
import { AnalysisResult, HardwareProfile } from "./types.js";
import { analyzeCodeStatic } from "./staticAnalyzer.js";

// Region Carbon Intensity Map
const REGION_CARBON_INTENSITY: Record<string, number> = {
  'us-central1': 360,
  'asia-east1': 620,
  'europe-west4': 180,
  'global': 450,
  'us-east1': 480
};

// Custom Error Types
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

export const analyzeAndOptimize = async (
  apiKey: string,
  code: string,
  hardware: HardwareProfile,
  scope: 'snippet' | 'module' = 'snippet',
  mock: boolean = false
): Promise<AnalysisResult> => {

  if (mock) {
      console.log("  > [System] Running in MOCK mode. Returning dummy analysis.");
      return {
          originalEnergyJoules: 1500,
          optimizedEnergyJoules: 1200,
          improvementPercentage: 20,
          carbonSavedGrams: 0.5,
          estimatedHourlyCost: 0.45,
          confidenceScore: 0.95,
          uncertaintyFactors: [],
          strategyAnalysis: "Mock strategy: Optimize convolutions.",
          tradeoffMetrics: {
              performanceScore: 80,
              costEfficiencyScore: 90,
              carbonEfficiencyScore: 85
          },
          assumptions: ["Mock Assumption 1"],
          citations: ["Mock Citation 1"],
          energy_model: "Mock Model",
          reasoning_trace: "Mock trace...",
          bottleneckAnalysis: "Mock bottleneck analysis.",
          impactAnalogy: "Like switching to LED bulbs.",
          recommendations: [
              { title: "Use Grouped Conv", gain: "20%", reasoning: "Reduces parameters.", category: "High" }
          ],
          optimizedCode: "# Mock optimized code\n" + code,
          breakdown: []
      };
  }

  if (!apiKey) {
      throw new GeminiError("No API Key provided.", false);
  }

  const ai = new GoogleGenAI({ apiKey: apiKey });

  // Step 1: Run Static Analysis
  const staticData = analyzeCodeStatic(code);
  const estimatedGFlops = staticData.estimatedFlops;
  const layerSummary = JSON.stringify(staticData.layerCounts);
  const structuralHighlights = staticData.structuralHighlights.map(h => h.label).join(", ");

  // Step 2: System Instruction
  const systemInstruction = `
    You are **DeepGreen AI**, an energy optimization agent powered by Gemini 3.
    
    ## TASK SCOPE: ${scope === 'module' ? 'FULL MODULE / PROJECT SCAN' : 'CODE SNIPPET ANALYSIS'}
    Target Hardware: ${hardware.name} (${hardware.type}).
    Target Region: ${hardware.region || 'Global Average'} (Carbon Intensity: ${hardware.carbonIntensity || 'Unknown'} gCO2/kWh).

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

  const textPrompt = `Analyze this PyTorch code for ${hardware.name} (ID: ${hardware.id}):\n${code}`;

  const parts: any[] = [{ text: textPrompt }];

  const tools: Tool[] = [
    { googleSearch: {} },
    { codeExecution: {} },
    {
      functionDeclarations: [{
        name: "calculate_carbon_footprint",
        description: "Calculate carbon footprint based on energy consumption and region.",
        parameters: {
          type: Type.OBJECT,
          properties: {
            energyJoules: { type: Type.NUMBER, description: "Total energy consumed in Joules" },
            region: { type: Type.STRING, description: "Data center region (e.g., us-central1)" }
          },
          required: ["energyJoules", "region"]
        }
      }]
    }
  ];

  return retryOperation(async () => {
    try {
      const chat = ai.chats.create({
        model: "gemini-2.0-flash-exp", // Updated model name for CLI context if needed, but keeping consistent or using latest known working
        config: {
          systemInstruction,
          tools: tools,
          // thinkingConfig: { 
          //   thinkingBudget: 1024 
          // },
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              reasoning_trace: { type: Type.STRING, description: "Structured technical audit including Search and Code Execution results." },
              assumptions: { type: Type.ARRAY, items: { type: Type.STRING }, description: "List technical assumptions" },
              citations: { type: Type.ARRAY, items: { type: Type.STRING }, description: "Sources for data" },
              energy_model: { type: Type.STRING, description: "How Joules were calculated from GFLOPs" },
              originalEnergyJoules: { type: Type.NUMBER },
              optimizedEnergyJoules: { type: Type.NUMBER },
              improvementPercentage: { type: Type.NUMBER },
              carbonSavedGrams: { type: Type.NUMBER },
              estimatedHourlyCost: { type: Type.NUMBER },
              costSavingsPer1MInference: { type: Type.NUMBER },
              confidenceScore: { type: Type.NUMBER },
              uncertaintyFactors: { type: Type.ARRAY, items: { type: Type.STRING } },
              benchmarkData: {
                type: Type.OBJECT,
                properties: {
                  found: { type: Type.BOOLEAN },
                  source: { type: Type.STRING },
                  device: { type: Type.STRING },
                  metric: { type: Type.STRING },
                  value: { type: Type.STRING }
                },
                required: ["found", "source", "device", "metric", "value"]
              },
              strategyAnalysis: { type: Type.STRING },
              bottleneckAnalysis: { type: Type.STRING },
              impactAnalogy: { type: Type.STRING },
              tradeoffMetrics: {
                type: Type.OBJECT,
                properties: {
                  performanceScore: { type: Type.NUMBER },
                  costEfficiencyScore: { type: Type.NUMBER },
                  carbonEfficiencyScore: { type: Type.NUMBER }
                }
              },
              recommendations: {
                type: Type.ARRAY,
                items: {
                  type: Type.OBJECT,
                  properties: {
                    title: { type: Type.STRING },
                    gain: { type: Type.STRING },
                    reasoning: { type: Type.STRING },
                    category: { type: Type.STRING, enum: ["High", "Medium", "Exploratory"] }
                  }
                }
              },
              optimizedCode: { type: Type.STRING },
              breakdown: {
                type: Type.ARRAY,
                items: {
                  type: Type.OBJECT,
                  properties: {
                    component: { type: Type.STRING },
                    percentage: { type: Type.NUMBER },
                    joules: { type: Type.NUMBER },
                    color: { type: Type.STRING }
                  }
                }
              }
            }
          }
        }
      });

      // Tool Execution Loop
      let currentMessage: any[] = parts;
      
      // We will loop until the model returns the final JSON response without function calls
      // However, the Node SDK 'sendMessage' might handle some of this, but 'tools' usually requires a loop.
      // For simplicity in CLI, we can emulate the loop or check if the SDK supports auto-tool-execution.
      // The @google/genai SDK v1.34 might handle tools differently?
      // Actually, let's stick to the loop pattern which is robust.
      
      while (true) {
        const result = await chat.sendMessage({ message: currentMessage });
        const response = result;
        
        // Check for function calls
        const functionCalls = response.functionCalls;
        
        if (functionCalls && functionCalls.length > 0) {
           const functionResponses = [];
           console.log("  > [Gemini] Calling tools:", functionCalls.map(fc => fc.name).join(", "));

           for (const call of functionCalls) {
                if (call.name === "calculate_carbon_footprint") {
                    const args = call.args as any;
                    const joules = args.energyJoules || 0;
                    const region = args.region || "global";
                    const intensity = REGION_CARBON_INTENSITY[region] || REGION_CARBON_INTENSITY['global'] || 450;
                    const kwh = joules / 3600000;
                    const grams = kwh * intensity;
                    
                    functionResponses.push({
                        id: call.id,
                        name: call.name,
                        response: { result: { carbonGrams: grams } }
                    });
                }
           }
           
           // If we handled calls, send back responses
           if (functionResponses.length > 0) {
               currentMessage = functionResponses.map(fr => ({
                   functionResponse: fr
               }));
               continue; // Loop again with tool outputs
           }
        }
        
        // If no function calls, or we couldn't handle them (shouldn't happen with our specific tool), we are done.
        // The response text should be our JSON.
        let text = "";
        
        // Try standard SDK helper if available (cast to any to avoid strict type issues with differing SDK versions)
        try {
            if (typeof (response as any).text === 'function') {
                text = (response as any).text();
            }
        } catch (e) { /* ignore */ }

        // Fallback to raw candidate structure
        if (!text && response.candidates && response.candidates[0] && response.candidates[0].content && response.candidates[0].content.parts) {
             text = response.candidates[0].content.parts.map((p:any) => p.text).join('');
        }
        
        if (!text) throw new GeminiError("Model failed to generate text response.", true);

        let cleanText = text.replace(/\[\[PHASE:[\s\S]*?\]\]/g, '');
        const firstBrace = cleanText.indexOf('{');
        const lastBrace = cleanText.lastIndexOf('}');
        
        if (firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace) {
            cleanText = cleanText.substring(firstBrace, lastBrace + 1);
        } else {
            cleanText = cleanText.trim();
        }

        try {
            return JSON.parse(cleanText) as AnalysisResult;
        } catch (e) {
            console.error("Malformed JSON:", cleanText);
            throw new GeminiError("Failed to parse analysis report.", false);
        }
      }

    } catch (error: any) {
      console.error("Gemini Failure:", error);
      throw error;
    }
  });
};
