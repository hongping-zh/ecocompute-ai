import React from 'react';
import { ArrowRight, Zap, DollarSign, Leaf, AlertTriangle, CheckCircle2 } from 'lucide-react';

const ORIGINAL_CODE = `import torch.nn as nn

class ResNetBlock(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        # ⚠️ Standard Conv (High Energy)
        self.conv1 = nn.Conv2d(in_c, out_c, 3, 1, 1)
        self.bn1 = nn.BatchNorm2d(out_c)
        self.relu = nn.ReLU()
        # ⚠️ Memory Intensive
        self.conv2 = nn.Conv2d(out_c, out_c, 3, 1, 1)
        
    def forward(self, x):
        # ⚠️ Separate ops = VRAM spikes
        x = self.conv1(x)
        x = self.bn1(x)
        return self.relu(x)`;

const OPTIMIZED_CODE = `import torch.nn as nn

class EcoResNetBlock(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()
        # ✅ Fused Operator (20% less DRAM)
        self.fused_cbr = nn.utils.fusion.fuse_conv_bn_relu(
            in_c, out_c, 3, 1, 1
        )
        # ✅ Grouped Conv (4x fewer FLOPs)
        self.conv2 = nn.Conv2d(out_c, out_c, 3, 1, 1, 
                              groups=4) 
        
    def forward(self, x):
        # ✅ Streamlined Execution
        return self.conv2(self.fused_cbr(x))`;

export const PromotionComparison: React.FC = () => {
  return (
    <div className="min-h-screen bg-[#0f0f16] flex items-center justify-center p-8 font-sans">
      <div className="flex flex-col md:flex-row gap-0 items-stretch max-w-6xl w-full rounded-3xl overflow-hidden shadow-2xl border border-gray-800">
        
        {/* Left: Original (Inefficient) */}
        <div className="flex-1 bg-[#1a1111] border-r border-red-900/30 p-8 relative group">
          <div className="absolute inset-0 bg-red-500/5 pointer-events-none" />
          
          <div className="relative z-10">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-red-500/20 rounded-lg">
                        <AlertTriangle className="w-6 h-6 text-red-500" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-red-100">Original Code</h2>
                        <p className="text-red-400 text-sm">Baseline Implementation</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-red-950/40 border border-red-500/20 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-red-300 text-xs uppercase font-bold tracking-wider mb-1">
                        <Zap className="w-3 h-3" /> Energy
                    </div>
                    <div className="text-2xl font-mono text-red-100">500 J</div>
                    <div className="text-xs text-red-400/60">Per Batch</div>
                </div>
                <div className="bg-red-950/40 border border-red-500/20 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-red-300 text-xs uppercase font-bold tracking-wider mb-1">
                        <DollarSign className="w-3 h-3" /> Cost
                    </div>
                    <div className="text-2xl font-mono text-red-100">$0.05</div>
                    <div className="text-xs text-red-400/60">Per Hour</div>
                </div>
            </div>

            <div className="bg-[#0a0a0a] rounded-xl border border-red-500/20 p-4 font-mono text-sm text-gray-300 overflow-hidden relative">
                <div className="absolute top-0 right-0 px-2 py-1 bg-red-500/20 text-red-400 text-[10px] font-bold rounded-bl">HIGH LATENCY</div>
                <pre>{ORIGINAL_CODE}</pre>
            </div>
          </div>
        </div>

        {/* Center: Divider & Action */}
        <div className="relative w-full md:w-0 flex items-center justify-center z-20">
            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 flex flex-col items-center gap-2">
                <div className="bg-gradient-to-r from-red-500 to-green-500 p-[2px] rounded-full shadow-[0_0_30px_rgba(34,197,94,0.4)]">
                    <div className="bg-[#11111b] p-3 rounded-full">
                        <ArrowRight className="w-8 h-8 text-white" />
                    </div>
                </div>
                <div className="bg-dark-900 border border-gray-700 px-4 py-1.5 rounded-full whitespace-nowrap shadow-xl">
                    <span className="text-sm font-bold bg-gradient-to-r from-eco-400 to-blue-400 bg-clip-text text-transparent">
                        EcoCompute Optimized
                    </span>
                </div>
            </div>
        </div>

        {/* Right: Optimized (Efficient) */}
        <div className="flex-1 bg-[#051108] border-l border-green-900/30 p-8 relative">
           <div className="absolute inset-0 bg-green-500/5 pointer-events-none" />
           
           <div className="relative z-10">
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-green-500/20 rounded-lg">
                        <Leaf className="w-6 h-6 text-green-500" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-green-100">Optimized Code</h2>
                        <p className="text-green-400 text-sm">DeepGreen Strategy Applied</p>
                    </div>
                </div>
                <div className="px-3 py-1 bg-green-500/20 text-green-400 text-xs font-bold rounded-full border border-green-500/30">
                    -60% CARBON
                </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-green-900/20 border border-green-500/20 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-green-300 text-xs uppercase font-bold tracking-wider mb-1">
                        <Zap className="w-3 h-3" /> Energy
                    </div>
                    <div className="text-2xl font-mono text-green-100">200 J</div>
                    <div className="text-xs text-green-400/60">Per Batch</div>
                </div>
                <div className="bg-green-900/20 border border-green-500/20 rounded-xl p-4">
                    <div className="flex items-center gap-2 text-green-300 text-xs uppercase font-bold tracking-wider mb-1">
                        <DollarSign className="w-3 h-3" /> Cost
                    </div>
                    <div className="text-2xl font-mono text-green-100">$0.02</div>
                    <div className="text-xs text-green-400/60">Per Hour</div>
                </div>
            </div>

            <div className="bg-[#0a0a0a] rounded-xl border border-green-500/30 p-4 font-mono text-sm text-gray-300 overflow-hidden relative shadow-[0_0_20px_rgba(34,197,94,0.1)]">
                <div className="absolute top-0 right-0 px-2 py-1 bg-green-500/20 text-green-400 text-[10px] font-bold rounded-bl">MAX EFFICIENCY</div>
                <pre>{OPTIMIZED_CODE}</pre>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
