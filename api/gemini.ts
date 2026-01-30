type HardwareProfile = {
  id: string;
  name: string;
  type: "GPU" | "TPU" | "CPU" | "Mobile";
  icon: string;
  efficiency: string;
  region?: string;
  carbonIntensity?: number;
};

function extractJson(text: string): unknown {
  const firstBrace = text.indexOf("{");
  const lastBrace = text.lastIndexOf("}");
  const sliced = firstBrace !== -1 && lastBrace !== -1 && lastBrace > firstBrace
    ? text.slice(firstBrace, lastBrace + 1)
    : text.trim();
  return JSON.parse(sliced);
}

export default async function handler(req: any, res: any) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method Not Allowed" });
    return;
  }

  const apiKey = process.env.GEMINI_API_KEY || process.env.API_KEY;
  if (!apiKey) {
    res.status(500).json({ error: "Missing GEMINI_API_KEY" });
    return;
  }

  const { code, hardware, scope, imagePngBase64 } = (req.body || {}) as {
    code?: string;
    hardware?: HardwareProfile;
    scope?: "snippet" | "module";
    imagePngBase64?: string;
  };

  if (!code || !hardware) {
    res.status(400).json({ error: "Missing code or hardware" });
    return;
  }

  const safeScope: "snippet" | "module" = scope === "module" ? "module" : "snippet";

  const systemInstruction = `You are DeepGreen AI, an energy optimization agent.
Return JSON only.
TASK_SCOPE=${safeScope}
TargetHardware=${hardware.name} (${hardware.type})
TargetRegion=${hardware.region || "global"}
CarbonIntensity=${hardware.carbonIntensity ?? "unknown"} gCO2/kWh

Required JSON keys:
reasoning_trace, assumptions, citations, energy_model,
originalEnergyJoules, optimizedEnergyJoules, improvementPercentage, carbonSavedGrams,
estimatedHourlyCost, costSavingsPer1MInference, confidenceScore, uncertaintyFactors,
benchmarkData, strategyAnalysis, bottleneckAnalysis, impactAnalogy, tradeoffMetrics,
recommendations, optimizedCode, breakdown`;

  const parts: any[] = [];
  if (imagePngBase64) {
    parts.push({
      inlineData: {
        mimeType: "image/png",
        data: imagePngBase64,
      },
    });
  }
  parts.push({
    text: imagePngBase64
      ? `Analyze the attached sketch/diagram for ${hardware.name}. Use it as the primary architecture reference. Code context:\n\n${code}`
      : `Analyze this PyTorch code for ${hardware.name} (ID: ${hardware.id}):\n${code}`,
  });

  const resp = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key=${encodeURIComponent(apiKey)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: systemInstruction }] },
        contents: [{ role: "user", parts }],
        generationConfig: {
          temperature: 0.2,
          responseMimeType: "application/json",
        },
      }),
    }
  );

  if (!resp.ok) {
    const txt = await resp.text();
    res.status(resp.status).json({ error: txt });
    return;
  }

  const data = (await resp.json()) as any;
  const text =
    data?.candidates?.[0]?.content?.parts?.map((p: any) => p?.text || "").join("") ||
    "";

  try {
    const parsed = extractJson(text);
    res.status(200).json(parsed);
  } catch {
    res.status(500).json({ error: "Malformed JSON from model", raw: text });
  }
}
