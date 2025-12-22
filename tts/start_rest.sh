#!/bin/bash
eval "$(conda shell.bash hook)"
DASHSCOPE_API_KEY=sk-509cc0f8f72b4f888d69854cbe250fb3
conda activate evoice && nohup python gen.py  >> tts.log 2>&1 &
echo "The rest server is running..."
