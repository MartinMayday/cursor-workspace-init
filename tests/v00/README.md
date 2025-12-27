# Test Repository v00

A simple multi-language test project for validating the cursor-workspace-init tool.

## Purpose

This repository is used to test the "analyze existing repo" functionality of the cursor-workspace-init tool. It contains a mix of Python and JavaScript code to trigger multiple analyzers.

## Languages

- Python 3.x
- JavaScript/Node.js

## Project Structure

```
v00/
├── README.md
├── package.json          # Node.js project configuration
├── requirements.txt      # Python dependencies
├── main.py              # Python entry point
├── index.js             # JavaScript entry point
└── src/
    ├── python/
    │   └── app.py       # Python application code
    └── javascript/
        └── app.js       # JavaScript application code
```

## Usage

This is a test repository. To test cursor-workspace-init:

```bash
cd tests/v00
python ../../cursor_init.py
```

The tool should detect:
- Python as primary language
- JavaScript as secondary language
- Project type: multi-language application
- Dependencies from both package.json and requirements.txt

