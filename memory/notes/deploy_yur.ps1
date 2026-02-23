```powershell
# ==========================================
# YUR AI: GENESIS DEPLOYMENT SCRIPT
# ==========================================
# This script creates the directory structure and seeds the 
# self-healing AI kernel files automatically.
# ==========================================

# 1. SETUP PATHS
$TargetDir = "$PWD\YUR_Genesis"
$WorkspaceDir = "$TargetDir\workspace"

Write-Host "Initializing YUR Genesis Deployment..." -ForegroundColor Cyan

# 2. CREATE DIRECTORIES
if (-not (Test-Path -Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir | Out-Null
    Write-Host "  [+] Created Root Directory: $TargetDir" -ForegroundColor Green
} else {
    Write-Host "  [!] Root Directory exists: $TargetDir" -ForegroundColor Yellow
}

if (-not (Test-Path -Path $WorkspaceDir)) {
    New-Item -ItemType Directory -Path $WorkspaceDir | Out-Null
    Write-Host "  [+] Created Workspace Directory: $WorkspaceDir" -ForegroundColor Green
}

# 3. SEED environment.yml
$EnvContent = @'
name: yur_genesis
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - pip
  - pip:
    - openai==0.28.0
    - termcolor
    - watchdog
'@

Set-Content -Path "$TargetDir\environment.yml" -Value $EnvContent
Write-Host "  [+] Seeded environment.yml" -ForegroundColor Green

# 4. SEED genesis.py (The AI Kernel)
# Note: We use single-quote Here-Strings so PowerShell ignores Python variables like $name
$GenesisContent = @'
import openai
import subprocess
import sys
import os
import time
from termcolor import colored

# ==========================================
# CONFIGURATION
# ==========================================

# !!! PASTE YOUR OPENAI API KEY BELOW !!!
openai.api_key = "PASTE_YOUR_KEY_HERE"

# Model Selection
MODEL = "gpt-4"

# ==========================================
# 1. THE COGNITIVE CORE (The Brain)
# ==========================================

def consult_oracle(system_prompt, user_input):
    """Sends a request to the AI model."""
    try:
        response = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1
        )
        return response.choices[0].message.content
    except Exception as e:
        print(colored(f"API Error: {e}", "red"))
        return None

# ==========================================
# 2. THE ENGINEER (Self-Deploying)
# ==========================================

def write_code(filename, code):
    """Writes code to the workspace folder."""
    # Ensure we write to the workspace directory to keep root clean
    filepath = os.path.join("workspace", filename)
    
    # Strip markdown
    clean_code = code.replace("```python", "").replace("```", "").strip()
    
    with open(filepath, 'w') as f:
        f.write(clean_code)
    print(colored(f"  [DEPLOY] Code written to {filepath}", "cyan"))
    return filepath

# ==========================================
# 3. THE HEALER (Self-Healing Loop)
# ==========================================

def execute_and_heal(filepath, attempt=1, max_retries=5):
    """Runs the code. If it fails, asks AI to fix it, overwrites, and retries."""
    if attempt > max_retries:
        print(colored("  [FATAL] Max retries reached. Healing failed.", "red"))
        return False

    print(colored(f"  [EXECUTE] Running {filepath} (Attempt {attempt})...", "yellow"))
    
    # Run the script
    result = subprocess.run([sys.executable, filepath], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(colored("  [SUCCESS] Execution successful.", "green"))
        print(f"  Output:\n{result.stdout}")
        return True
    else:
        print(colored("  [FAILURE] Crash detected. Initiating Self-Healing...", "red"))
        error_log = result.stderr
        print(f"  Error Log: {error_log.strip()}")
        
        # Read broken code
        with open(filepath, 'r') as f:
            broken_code = f.read()
        
        # Consult Oracle for a fix
        system_prompt = "You are an AI Self-Healing Engine. Rewrite the python script to fix the error. Return ONLY code."
        prompt = f"BROKEN CODE:\n{broken_code}\n\nERROR LOG:\n{error_log}\n\nFIXED CODE:"
        
        print(colored("  [HEALING] Synthesizing patch...", "magenta"))
        fixed_code = consult_oracle(system_prompt, prompt)
        
        if fixed_code:
            # Clean markdown again just in case
            fixed_code = fixed_code.replace("```python", "").replace("```", "").strip()
            with open(filepath, 'w') as f:
                f.write(fixed_code)
            
            return execute_and_heal(filepath, attempt + 1, max_retries)

# ==========================================
# 4. THE ARCHITECT (Self-Reasoning)
# ==========================================

def autonomous_loop(objective):
    print(colored(f"\nOBJECTIVE: {objective}", "blue", attrs=['bold']))
    
    # Plan
    print(colored("  [PLANNING] Defining architecture...", "blue"))
    plan = consult_oracle(
        "You are an Autonomous Architect. Break the objective into a filename and description.",
        f"Objective: {objective}. \nReturn strictly in this format: filename.py | description"
    )
    
    if not plan or "|" not in plan:
        print(colored("  [ERROR] Planning failed.", "red"))
        return

    filename, description = plan.split("|", 1)
    filename = filename.strip()
    
    # Generate Code
    print(colored(f"  [CODING] Generating {filename}...", "blue"))
    code = consult_oracle(
        "You are a Python Expert. Write a script to achieve the description. Return ONLY code.",
        f"Description: {description}"
    )
    
    # Deploy & Run
    filepath = write_code(filename, code)
    execute_and_heal(filepath)

if __name__ == "__main__":
    # Ensure workspace exists
    if not os.path.exists("workspace"):
        os.makedirs("workspace")

    # DEFINE YOUR GOAL HERE
    user_objective = "Create a script that calculates the first 10 Fibonacci numbers and saves them to fib.txt"
    
    autonomous_loop(user_objective)
'@

Set-Content -Path "$TargetDir\genesis.py" -Value $GenesisContent
Write-Host "  [+] Seeded genesis.py" -ForegroundColor Green

# 5. FINAL INSTRUCTIONS
Write-Host "`nDEPLOYMENT COMPLETE." -ForegroundColor Cyan
Write-Host "---------------------------------------------------"
Write-Host "NEXT STEPS:" -ForegroundColor White
Write-Host "1. Open Miniconda (Anaconda Prompt)."
Write-Host "2. Run: cd $TargetDir"
Write-Host "3. Run: conda env create -f environment.yml"
Write-Host "4. Run: conda activate yur_genesis"
Write-Host "5. Edit genesis.py and add your OpenAI API Key."
Write-Host "6. Run: python genesis.py"
Write-Host "---------------------------------------------------"
```