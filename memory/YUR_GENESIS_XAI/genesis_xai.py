import os
import sys
import subprocess
import time
import requests
from dotenv import load_dotenv
from termcolor import colored

# --- CONFIGURATION ---
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")
XAI_BASE_URL = "https://api.x.ai/v1"
XAI_MODEL = "grok-3"

if not XAI_API_KEY:
    print(colored("[CRITICAL] XAI_API_KEY not found in .env file.", "red"))
    print(colored("Please edit the .env file with your XAI key.", "yellow"))
    sys.exit(1)

class YUR_Agent:
    def __init__(self):
        self.max_retries = 5
        self.headers = {
            "Authorization": f"Bearer {XAI_API_KEY}",
            "Content-Type": "application/json"
        }
        print(colored(">>> YUR COGNITIVE CORE ONLINE (XAI GROK-3)", "cyan", attrs=["bold"]))

    def consult_oracle(self, system_role, user_input):
        """XAI API call (REST-based, no SDK needed)."""
        try:
            payload = {
                "messages": [
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": user_input}
                ],
                "model": XAI_MODEL,
                "stream": False,
                "temperature": 0.2
            }
            response = requests.post(
                f"{XAI_BASE_URL}/chat/completions",
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                print(colored(f"[XAI API ERROR] {response.status_code}: {response.text}", "red"))
                return None
        except Exception as e:
            print(colored(f"[API EXCEPTION] {str(e)}", "red"))
            return None

    def extract_code(self, response_text):
        """Extract Python code from Markdown blocks."""
        if not response_text:
            return ""
        if "```python" in response_text:
            return response_text.split("```python")[1].split("```")[0].strip()
        elif "```" in response_text:
            return response_text.split("```")[1].split("```")[0].strip()
        return response_text.strip()

    def execute_and_heal(self, filename, goal_description):
        """Self-Healing Loop: Execute -> Catch Error -> Heal -> Retry."""
        attempt = 0
        
        while attempt < self.max_retries:
            attempt += 1
            print(colored(f"\n[EXECUTION] Attempt {attempt}/{self.max_retries} for {filename}...", "yellow"))

            try:
                result = subprocess.run(
                    [sys.executable, filename], 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
            except subprocess.TimeoutExpired:
                print(colored("[TIMEOUT] Script execution exceeded 30 seconds.", "red"))
                continue
            except Exception as e:
                print(colored(f"[SYSTEM ERROR] {e}", "red"))
                return False

            if result.returncode == 0:
                print(colored(f"[SUCCESS] Script executed successfully.", "green"))
                print(f"--- OUTPUT ---\n{result.stdout}\n--------------")
                return True
            
            error_msg = result.stderr
            print(colored(f"[FAILURE] Runtime Error:\n{error_msg}", "red"))
            
            print(colored("[HEALER] Diagnosing via XAI Grok-3...", "magenta"))
            
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    current_code = f.read()
            except FileNotFoundError:
                print(colored("[ERROR] Target file not found.", "red"))
                return False

            fix_prompt = f"""
You are the HEALER. The Python script below failed during execution.

GOAL: {goal_description}

CURRENT CODE:
{current_code}

ERROR TRACEBACK:
{error_msg}

INSTRUCTIONS:
1. Analyze the error and find the root cause.
2. Fix the code logic, syntax, or imports.
3. Return ONLY the corrected Python code in ```python blocks.
4. No explanations, only code.
"""
            
            response = self.consult_oracle(
                "You are an expert Python Debugger and System Architect specializing in self-healing code.",
                fix_prompt
            )
            
            if not response:
                print(colored("[HEALER] No response from XAI. Retrying...", "red"))
                continue
                
            new_code = self.extract_code(response)
            
            if not new_code:
                print(colored("[HEALER] Failed to extract code. Retrying...", "red"))
                continue

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(new_code)
            print(colored("[HEALER] Patch applied. Retrying execution...", "cyan"))
        
        print(colored("[FATAL] Max retries reached. Manual intervention required.", "red"))
        return False

    def genesis_loop(self):
        """Main Bootstrapping Sequence."""
        
        mission = """Create a Python script named 'yur_financial_model.py' that runs a comprehensive Wealth Abundance Velocity (WAV) analysis:

PARAMETERS:
- Initial capital: $100 billion
- Time horizon: 10 years
- Retained yield range: 1% and 2% (run both scenarios)
- Effective annual growth: 65%
- Growth sensitivity: 60%, 65%, 70% (show comparison table)

OUTPUT REQUIREMENTS:
1. Year-by-year balance table for each retained yield scenario (1% and 2%)
2. Verify final balance reaches ~$15 trillion at 65% growth
3. Sensitivity analysis showing outcomes at 60%, 65%, 70% annual growth
4. Format as clean tables with proper currency formatting
5. Summary statistics at the end

Use only standard library (no external dependencies). Return ONLY code."""
        
        target_file = "yur_financial_model.py"

        print(colored(f"[ARCHITECT] Designing solution for enterprise-scale WAV model...", "blue"))
        prompt = f"Write a complete, production-ready Python script to: {mission}. Use only standard library. Return ONLY code in ```python blocks."
        
        raw_response = self.consult_oracle(
            "You are a Senior Python Architect designing mission-critical systems.",
            prompt
        )
        
        if not raw_response:
            print(colored("[CRITICAL] Failed to get initial code from XAI.", "red"))
            return False
            
        code = self.extract_code(raw_response)
        
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(code)
        print(colored(f"[ENGINEER] Initial code written to {target_file}", "blue"))

        return self.execute_and_heal(target_file, mission)

if __name__ == "__main__":
    agent = YUR_Agent()
    success = agent.genesis_loop()
    sys.exit(0 if success else 1)
