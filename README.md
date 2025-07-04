# Kratos Element Test Suite
The Kratos Element Test Suite, a collection of programs and scripts designed to model the laboratory within the geotechnical laboratories. This repository will be extended in the future with additional tooling to support advanced analysis workflows, such as parameter estimation.

**Note**: Due to limitations with dependent packages, this suite can only be installed on machines with Python 3.10 - 3.12.

## Requirements
- Python 3.10 - 3.12
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

Activate the environment:
```bash
element_env\Scripts\activate
```
After activation of the virtual environment, the name of your environment (element_env) should be visible in parentheses at the start of the line.

To install the library into your current and active Python environment, use:
```bash
pip install git+https://github.com/Deltares-research/KratosElementTestSuite
```

## Running
Once installed, you can run the Element Test Suite by:
```bash
startElementTest
```

**Note**: For this Alpha release, we are aware of some scaling issues. If you scale the window to a small size, or if the scale option of your display settings is set to a value higher than 125%, the tool is not usable.
