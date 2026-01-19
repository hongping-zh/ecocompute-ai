
import { program } from 'commander';
import chalk from 'chalk';
import * as fs from 'fs';
import * as path from 'path';
import * as glob from 'glob';
import dotenv from 'dotenv';
import { analyzeAndOptimize } from './geminiService.js';
import { HardwareProfile, RecommendationItem, AnalysisResult } from './types.js';
import * as core from '@actions/core';
import * as github from '@actions/github';

// Load environment variables
dotenv.config({ path: '.env.local' });
dotenv.config(); // Also try default .env

const DEFAULT_HARDWARE: HardwareProfile = {
  id: 'nvidia-h100',
  name: 'NVIDIA H100',
  type: 'GPU',
  icon: 'cpu', // Placeholder
  efficiency: 'High',
  region: 'us-central1',
  carbonIntensity: 360
};

// GitHub Action Logic
async function runAction() {
  try {
    const apiKey = core.getInput('gemini_key', { required: true });
    const githubToken = core.getInput('github_token', { required: true });
    
    // In Actions, workspace is usually in GITHUB_WORKSPACE or current dir
    const targetDir = process.env.GITHUB_WORKSPACE || '.';
    
    console.log(`Starting EcoCompute Action in ${targetDir}`);

    const files = glob.sync(`${targetDir}/**/*.py`, { ignore: ['**/node_modules/**', '**/venv/**', '**/env/**'] });
    
    if (files.length === 0) {
      console.log('No Python files found.');
      return;
    }

    const octokit = github.getOctokit(githubToken);
    const context = github.context;

    // Only comment on PRs
    if (!context.payload.pull_request) {
      console.log('Not a Pull Request. Skipping comments.');
    }

    let commentBody = "## 🌿 EcoCompute Audit Report\n\n";
    let hasIssues = false;

    for (const file of files) {
      const code = fs.readFileSync(file, 'utf-8');
      try {
        // Run analysis (using snippet scope for now)
        const result = await analyzeAndOptimize(apiKey, code, DEFAULT_HARDWARE, 'snippet');

        if (result.recommendations && result.recommendations.length > 0) {
           hasIssues = true;
           const relPath = path.relative(targetDir, file);
           
           commentBody += `### 📄 File: \`${relPath}\`\n`;
           if (result.estimatedHourlyCost) {
             commentBody += `**💸 Est. Waste:** $${result.estimatedHourlyCost.toFixed(4)} / hr\n`;
           }
           
           // Construct the requested alert format
           // "🚨 EcoCompute Alert This PR introduces a ResNet-50 Bottleneck on line 42. 💸 Est. Waste: $42.50 / 1M inferences. 🛠️ Fix: [Click to see optimized code]"
           
           if (result.bottleneckAnalysis) {
              commentBody += `> 🚨 **EcoCompute Alert**: ${result.bottleneckAnalysis}\n`;
           }
           
           result.recommendations.forEach(rec => {
              commentBody += `- **[${rec.category}]** ${rec.title}: ${rec.gain} _(${rec.reasoning})_\n`;
           });

           if (result.optimizedCode) {
              commentBody += `\n<details>\n<summary>🛠️ Fix: Click to see optimized code</summary>\n\n\`\`\`python\n${result.optimizedCode}\n\`\`\`\n</details>\n\n`;
           }
           
           commentBody += `---\n`;
        }
      } catch (err: any) {
        core.error(`Failed to analyze ${file}: ${err.message}`);
      }
    }

    if (hasIssues && context.payload.pull_request) {
       await octokit.rest.issues.createComment({
         ...context.repo,
         issue_number: context.payload.pull_request.number,
         body: commentBody
       });
       core.setFailed("EcoCompute found expensive patterns. Please review the report.");
    } else {
       console.log("No significant energy issues found.");
    }

  } catch (error: any) {
    core.setFailed(error.message);
  }
}

async function main() {
  // Detect if running in GitHub Actions
  if (process.env.GITHUB_ACTIONS === 'true') {
     await runAction();
     return;
  }

  program
    .name('ecocompute')
    .description('EcoCompute AI Gatekeeper - Optimize your AI models for energy efficiency')
    .version('1.0.0');

  program
    .command('scan <target>')
    .description('Scan a file or directory for energy optimization')
    .option('-k, --key <key>', 'Gemini API Key')
    .option('-t, --threshold <cost>', 'Estimated cost threshold to fail CI', parseFloat)
    .option('--mock', 'Run in mock mode without API calls')
    .action(async (target, options) => {
      const apiKey = options.key || process.env.GEMINI_API_KEY || process.env.API_KEY || (options.mock ? 'mock-key' : undefined);
      
      if (!apiKey && !options.mock) {
        console.error(chalk.red('Error: Gemini API Key is required. Set GEMINI_API_KEY env var or use --key option.'));
        process.exit(1);
      }

      const files: string[] = [];
      
      if (fs.statSync(target).isDirectory()) {
         // Glob pattern to find python files
         const found = glob.sync(`${target}/**/*.py`);
         files.push(...found);
      } else {
         files.push(target);
      }

      if (files.length === 0) {
        console.log(chalk.yellow('No Python files found to scan.'));
        return;
      }

      console.log(chalk.blue(`Scanning ${files.length} file(s)...`));

      let totalWaste = 0;
      let hasCriticalIssues = false;

      for (const file of files) {
        const code = fs.readFileSync(file, 'utf-8');
        console.log(chalk.cyan(`\nAnalyzing ${file}...`));

        try {
          const result = await analyzeAndOptimize(apiKey!, code, DEFAULT_HARDWARE, 'snippet', options.mock);
          
          if (result.confidenceScore < 0.5) {
             console.log(chalk.yellow(`  Warning: Low confidence analysis (${(result.confidenceScore * 100).toFixed(0)}%)`));
          }

          console.log(chalk.green(`  ✓ Analysis Complete`));
          if (result.estimatedHourlyCost) {
            console.log(`  💸 Est. Cost: $${result.estimatedHourlyCost.toFixed(4)}/hr`);
            // Simple accumulation for threshold check (logic can be refined)
            totalWaste += result.estimatedHourlyCost; 
          }
          
          if (result.improvementPercentage > 0) {
              console.log(chalk.green(`  ⚡ Potential Energy Savings: ${result.improvementPercentage}%`));
              console.log(chalk.green(`  🌿 Carbon Saved: ${result.carbonSavedGrams.toFixed(4)}g`));
          }

          if (result.bottleneckAnalysis && result.bottleneckAnalysis.includes("CRITICAL BUG")) {
             console.log(chalk.red(`  🚨 ${result.bottleneckAnalysis}`));
             hasCriticalIssues = true;
          } else if (result.recommendations && result.recommendations.length > 0) {
              console.log(chalk.white(`  Recommendations:`));
              result.recommendations.forEach((rec: RecommendationItem) => {
                  console.log(`    - [${rec.category}] ${rec.title}: ${rec.gain}`);
              });
          }

        } catch (error: any) {
          console.error(chalk.red(`  x Failed to analyze ${file}: ${error.message}`));
        }
      }

      // Threshold check
      if (options.threshold && totalWaste > options.threshold) {
          console.error(chalk.red(`\nFAILURE: Estimated waste ($${totalWaste.toFixed(2)}) exceeds threshold ($${options.threshold}).`));
          process.exit(1);
      }

      if (hasCriticalIssues) {
          console.error(chalk.red(`\nFAILURE: Critical architecture bugs detected.`));
          process.exit(1);
      }
    });

  program.parse();
}

main();
