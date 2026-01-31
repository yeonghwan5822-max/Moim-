#!/bin/bash
# 프로젝트 폴더로 이동
cd ~/Desktop/moim\ 번역기\ 프로젝트 2>/dev/null || cd ~/Documents/moim\ 번역기\ 프로젝트

# 실행 메시지 출력
echo "🚀 MOIM 번역기를 실행합니다..."
echo "잠시만 기다려주세요..."

# 앱 실행
python3 -m streamlit run backend/streamlit_app.py
