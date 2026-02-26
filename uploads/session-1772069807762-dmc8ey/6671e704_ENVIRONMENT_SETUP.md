# Environment Setup Guide

## Miniconda Installation

Your Python environment is configured to use:
```
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3
```

**Python Version:** 3.13.9

## Installing Dependencies

All required dependencies have been installed via pip. The `environment.yml` file contains the dependency specification.

### To recreate the environment on a fresh system:

```powershell
# Navigate to the project directory
cd C:\XAI_GROK_GENESIS

# Install all dependencies (one-time setup)
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -m pip install -r requirements.txt
```

## Installed Packages

| Package | Version | Purpose |
|---------|---------|---------|
| requests | 2.32.5 | HTTP client for xAI API calls |
| PyQt5 | 5.15.11 | GUI framework (vault citadel, vault interface) |
| pyttsx3 | 2.99 | Text-to-speech engine |
| numpy | 2.4.2 | Numerical computing (lattice operations) |
| cryptography | 46.0.4 | Cryptographic primitives |
| openai | 2.17.0 | OpenAI SDK (Tkinter oracle gui) |
| python-dotenv | 1.1.0 | Environment variable management (.env) |
| colorama | 0.4.6 | Terminal color output |
| termcolor | 3.3.0 | Colored terminal text |

## Running the Applications

### Option 1: Vault Citadel (PyQt5 Dashboard)
```powershell
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe yur_vault_citadel.py
```

### Option 2: Vault Interface (PyQt5 Alternative)
```powershell
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe yur_vault_interface.py
```

### Option 3: Oracle GUI (Tkinter)
```powershell
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe yur_oracle_gui.py
```

### Option 4: Multi-Kernel Orchestrator
```powershell
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe multi_kernel_orchestrator.py
```

## Adding the Python Executable to PATH (Optional)

To run Python directly without the full path:

```powershell
$env:PATH += ";C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\Scripts"
$env:PATH += ";C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3"
```

Add these to your PowerShell profile (`$PROFILE`) for permanent effect.

## Environment Variables

The `.env` file contains:
- `XAI_API_KEY` - Your xAI Grok API key (loaded by `python-dotenv`)

Ensure `.env` is **NEVER committed** to version control.

## Troubleshooting

**ImportError for PyQt5 or pyttsx3?**
```powershell
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -m pip install --force-reinstall PyQt5 pyttsx3
```

**Need to verify installation?**
```powershell
C:\Users\Jeremy Gosselin\OneDrive\Neo3\miniconda3\python.exe -c "import PyQt5, numpy, cryptography; print('All core dependencies loaded!')"
```

## Last Updated
February 5, 2026
