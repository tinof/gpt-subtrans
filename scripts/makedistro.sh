#!/bin/bash

source envsubtrans/bin/activate
pip install -r requirements.txt
pip install --upgrade openai
pip install --upgrade google-genai
pip install --upgrade anthropic
pip install --upgrade mistralai
pip install --upgrade boto3 # Keep boto3 for Bedrock provider

pyinstaller --noconfirm --additional-hooks-dir="PySubtitleHooks" --add-data "instructions*:instructions/" --add-data "LICENSE:." scripts/llm-subtrans.py # Removed theme/asset/icon data, changed entry point
