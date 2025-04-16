#!/bin/bash

source ./envsubtrans/bin/activate
pip3 install --upgrade pip
pip install --upgrade pyinstaller
pip install --upgrade PyInstaller pyinstaller-hooks-contrib
pip install --upgrade setuptools
pip install --upgrade jaraco.text
pip install --upgrade charset_normalizer
pip install --upgrade -r requirements.txt
pip install --upgrade openai
pip install --upgrade google-genai
pip install --upgrade anthropic
pip install --upgrade mistralai

# Removed boto3 uninstall (not in requirements)
# Removed unit test execution (tests removed)

./envsubtrans/bin/pyinstaller --noconfirm \
    --additional-hooks-dir="PySubtitleHooks" \
    --paths="./envsubtrans/lib" \
    # Removed --add-data for theme/ and assets/
    --add-data "instructions*:instructions/" \
    --add-data "LICENSE:." \
    --noconfirm \
    scripts/llm-subtrans.py # Changed entry point to generic CLI script
