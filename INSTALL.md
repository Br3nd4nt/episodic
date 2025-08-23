# 📦 Installing episodic

## Requirements

- Python 3.7 or higher
- pip (Python package manager)

## Installation Methods

### 1. Install from Source Code (Recommended)

```bash
# Clone repository
git clone https://github.com/br3nd4nt/episodic.git
cd episodic

# Install in development mode
pip install -e .
```

### 2. Manual Dependency Installation

```bash
# Install required packages
pip install click requests beautifulsoup4 lxml colorama

# Run script directly
python episodic.py --help
```

### 3. Install via requirements.txt

```bash
# Install all dependencies
pip install -r requirements.txt

# Run script
python episodic.py --help
```

## Verify Installation

After installation, verify that the command works:

```bash
# Check version
episodic --version

# Check help
episodic --help
```

## Installation on Different Platforms

### macOS

```bash
# Via Homebrew (if Python is installed)
brew install python3
pip3 install -e .

# Or via pyenv
pyenv install 3.12.0
pyenv global 3.12.0
pip install -e .
```

### Linux (Ubuntu/Debian)

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip

# Install episodic
pip3 install -e .
```

### Windows

```bash
# Install via PowerShell
python -m pip install -e .

# Or via Command Prompt
pip install -e .
```

## Troubleshooting

### Problem: "command not found: episodic"

```bash
# Check if pip installed the script in PATH
which episodic

# If not found, add to PATH or use python -m
python -m episodic --help
```

### Problem: "ModuleNotFoundError"

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Or reinstall completely
pip uninstall episodic
pip install -e .
```

### Problem: "Permission denied"

```bash
# Use --user flag
pip install --user -e .

# Or use virtual environment
python -m venv episodic_env
source episodic_env/bin/activate  # Linux/macOS
# episodic_env\Scripts\activate   # Windows
pip install -e .
```

## Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv episodic_env

# Activate
source episodic_env/bin/activate  # Linux/macOS
# episodic_env\Scripts\activate   # Windows

# Install
pip install -e .

# Deactivate
deactivate
```

## Updating

```bash
# Update from repository
git pull origin main
pip install -e . --upgrade
```

## Uninstalling

```bash
# Remove package
pip uninstall episodic

# Remove dependencies (if not used by other projects)
pip uninstall click requests beautifulsoup4 lxml colorama
```