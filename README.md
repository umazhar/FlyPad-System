# FlyPadUI and STROBE

## Overview
FlyPadUI (Sip TRiggered Optogenetic Behavior Enclosure) is a Python-based user interface for tracking fly sips, calculating preference indices, and providing a convenient graphical interface for data analysis. The software connects to the STROBE device to record and analyze feeding behavior in flies.

The original STROBE UI was built in Visual Studio 2012 in C++ on Windows 10 and required installation of Qt 5.11 to compile. The current Python-based version maintains compatibility with the STROBE device while providing improved usability and analysis capabilities.


## Requirements
- Python (latest version)
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository:
```bash
git clone https://github.com/umazhar/STROBE.git
cd /SOFTWARE/STROBE_UI
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main application:
```bash
python main.py
```

All output data will be stored in the `output` folder.

## File Structure
```
/SOFTWARE/STROBE_UI/
├── main.py           # Main application entry point
├── requirements.txt  # Dependencies
├── venv/             # Virtual environment (generated on setup)
└── output/           # Output data directory
```