import os
import sys
import subprocess
import json
import requests
from dotenv import load_dotenv
from termcolor import colored

# --- CONFIGURATION ---
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")

if not XAI_API_KEY:
    print(colored("[CRITICAL] XAI_API_KEY not found in .env file.", "red"))
    print(colored("Please edit the .env file in this directory with your key.", "yellow"))
    sys.exit(1)

# --- GROK API CONFIGURATION ---
GROK_API_URL = "https://api.x.ai/v1/chat/completions"
GROK_MODEL = "grok-3"  # Latest Grok model available

# --- THE TRINITY: ARCHITECT, ENGINEER, HEALER ---

class GROK_Agent:
    def __init__(self):
        self.max_retries = 5
        self.api_key = XAI_API_KEY
        print(colored(">>> XAI GROK COGNITIVE CORE ONLINE", "cyan", attrs=["bold"]))

    def consult_oracle(self, system_role, user_input):
        """Interacts with Grok API using REST endpoint."""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": GROK_MODEL,
                "messages": [
                    {"role": "system", "content": system_role},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.2,
                "max_tokens": 4096
            }
            
            response = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(colored(f"[API ERROR] {str(e)}", "red"))
            return None

    def extract_code(self, response_text):
        """Extracts Python code from Markdown blocks ensuring clean execution."""
        if not response_text:
            return ""
        if "```python" in response_text:
            return response_text.split("```python")[1].split("```")[0].strip()
        elif "```" in response_text:
            return response_text.split("```")[1].split("```")[0].strip()
        return response_text.strip()

    def execute_and_heal(self, filename, goal_description):
        """
        The Self-Healing Loop: 
        1. Executes code.
        2. Catches stderr on failure.
        3. Feeds traceback to Grok.
        4. Patches file.
        5. Repeats.
        """
        attempt = 0
        
        while attempt < self.max_retries:
            attempt += 1
            print(colored(f"\n[EXECUTION] Attempt {attempt}/{self.max_retries} for {filename}...", "yellow"))

            # 1. Run the script in a subprocess
            try:
                result = subprocess.run(
                    [sys.executable, filename], 
                    capture_output=True, 
                    text=True,
                    encoding="utf-8"
                )
            except Exception as e:
                print(colored(f"[SYSTEM ERROR] Subprocess failed to launch: {e}", "red"))
                return False

            # 2. Check for success
            if result.returncode == 0:
                print(colored(f"[SUCCESS] Script executed successfully.", "green"))
                print(f"--- OUTPUT ---\n{result.stdout}\n--------------")
                return True
            
            # 3. Handle Failure (The "Healer" Logic)
            error_msg = result.stderr
            print(colored(f"[FAILURE] Runtime Error Detected:\n{error_msg}", "red"))
            
            print(colored("[HEALER] Diagnosing and patching via Grok...", "magenta"))
            
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    current_code = f.read()
            except FileNotFoundError:
                print(colored("[ERROR] Target file vanished.", "red"))
                return False

            # 4. Consult Grok for a fix
            fix_prompt = f"""
            You are the HEALER. The Python script below failed during execution.
            
            GOAL: {goal_description}
            
            CURRENT CODE:
            {current_code}
            
            ERROR TRACEBACK:
            {error_msg}
            
            INSTRUCTIONS:
            1. Analyze the traceback to find the root cause.
            2. Fix the logic, syntax, or import errors.
            3. Return ONLY the full, corrected Python code inside ```python blocks.
            4. Do not offer explanations, just the code.
            """
            
            response = self.consult_oracle("You are an expert Python Debugger and Systems Architect.", fix_prompt)
            new_code = self.extract_code(response)
            
            if not new_code:
                print(colored("[HEALER] Failed to extract code from response. Retrying...", "red"))
                continue

            # 5. Overwrite and Retry
            with open(filename, "w", encoding="utf-8") as f:
                f.write(new_code)
            print(colored("[HEALER] Patch applied. Retrying execution...", "cyan"))
        
        print(colored("[FATAL] Max retries reached. Manual intervention required.", "red"))
        return False

    def genesis_loop(self):
        """The Main Bootstrapping Sequence."""
        
        # Define the Mission
        mission = "Create a Python script named \"neural_net_simple.py\" that demonstrates a simple feedforward neural network using only standard library (numpy alternative: manual matrix operations). Logic: Create 3-layer network, forward propagation, basic backpropagation on dummy data, print loss reduction over 20 epochs."
        target_file = "neural_net_simple.py"

        # Phase 1: The Architect & Engineer
        print(colored(f"[ARCHITECT] Designing solution for: {mission}", "blue"))
        prompt = f"Write a complete, runnable Python script to: {mission}. Use only standard library. Return ONLY code."
        
        raw_response = self.consult_oracle("You are a Senior Python Architect specialized in AI systems.", prompt)
        code = self.extract_code(raw_response)
        
        with open(target_file, "w", encoding="utf-8") as f:
            f.write(code)
        print(colored(f"[ENGINEER] Initial code written to {target_file}", "blue"))

        # Phase 2: The Execution & Healing
        self.execute_and_heal(target_file, mission)

if __name__ == "__main__":
    agent = GROK_Agent()
    agent.genesis_loop()
