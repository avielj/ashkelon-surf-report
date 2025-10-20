<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->
# Ashkelon Wave Forecast Project

This is a Python application that scrapes wave data from 4surfers.co.il specifically for Israeli beaches, with a focus on Ashkelon wave forecasting.

## Project Status: ✅ COMPLETED

- ✅ Project structure created
- ✅ Dependencies installed (Playwright, BeautifulSoup, pandas, etc.)
- ✅ Virtual environment configured  
- ✅ Wave forecast functionality implemented
- ✅ 4surfers.co.il integration working
- ✅ VS Code tasks configured
- ✅ Documentation complete

## Quick Start

1. **Test the application**:
   ```bash
   source venv/bin/activate
   python test_forecast.py
   ```

2. **Run interactively**:
   ```bash
   source venv/bin/activate
   python wave_forecast.py
   ```

3. **Use VS Code tasks**: Press `Cmd+Shift+P` → "Tasks: Run Task" → Choose "Test Forecast" or "Run Ashkelon Forecast"

## Key Features

- ✅ Scrapes real wave data from 4surfers.co.il
- ✅ Supports all Israeli beaches
- ✅ Hebrew language support
- ✅ Automated browser interaction with Playwright
- ✅ JSON data export
- ✅ Debug screenshots
- ✅ Comprehensive error handling

## Files Overview

- `wave_forecast.py` - Main application with 4surfers.co.il integration
- `test_forecast.py` - Test script for verification
- `requirements.txt` - Python dependencies
- `venv/` - Virtual environment (configured and ready)
- `.vscode/tasks.json` - VS Code tasks for easy running

## Current Status
The project is fully functional and successfully retrieves wave forecast data from 4surfers.co.il for Ashkelon. The test script confirms the connection works and data is being extracted.