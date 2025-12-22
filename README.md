# Kratos Element Test Suite
The Kratos Element Test Suite, a collection of programs and scripts designed to model the laboratory within the geotechnical laboratories. This repository will be extended in the future with additional tooling to support advanced analysis workflows, such as parameter estimation.

**Note**: Due to limitations with dependent packages, this suite can only be installed on machines with Python 3.10 - 3.14.

## Requirements
- Python 3.10 - 3.14
[Download for Windows](https://www.python.org/downloads/windows/)
- Git
[Download for Windows](https://git-scm.com/downloads/win)

## Installation
To keep your system clean and avoid conflicts, it's recommended to set up and run the Element Test Suite inside a virtual environment.
From a blank Command Prompt (not Anaconda Prompt or PowerShell):

Create a virtual environment (Name of this Python environment is element_env)
```bash
python -m venv element_env 
```
_(If you have multiple Python versions, you can replace `python` with `py -3.13` in the command above —[see here](https://docs.python.org/3/using/windows.html#python-launcher-for-windows)— assuming Python 3.13 is available on your system.)_

Activate the environment:
```bash
element_env\Scripts\activate
```
After activation of the virtual environment, the name of your environment (element_env) should be visible in parentheses at the start of the line.

To install the library into your current and active Python environment, use:
```bash
pip install git+https://github.com/Deltares-research/KratosElementTestSuite
```
Once installed, you can run the Element Test Suite by:
```bash
startElementTest
```
## Running after installation
Please make sure that the virtual environment is active before running the suite (the name of your environment `element_env` should be visible in parentheses at the start of the line.)
After activating the virtual environment, you can run the Element Test Suite by:
```bash
startElementTest
```

**Note**: For proper rendering of the user interface, your display scaling must be set to 125% or lower. The interface may not render correctly at higher scaling settings (e.g. 150% or above).
