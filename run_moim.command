#!/bin/bash
cd ~/Desktop/moim\ 번역기\ 프로젝트 2>/dev/null || cd ~/Documents/moim\ 번역기\ 프로젝트
echo "🚀 MOIM 번역기를 실행합니다..."
python3 -m streamlit run backend/streamlit_app.py
