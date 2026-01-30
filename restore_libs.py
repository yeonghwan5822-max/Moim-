import os

# 1. requirements.txt 복구
# deepl: 번역기 필수
# chromadb, soynlp: OOV 분석기 필수
# (만약 설치가 너무 오래 걸리면 chromadb는 나중에 뺄 수도 있습니다)
req_content = """streamlit==1.31.0
requests
beautifulsoup4
deepl
python-dotenv
chromadb
soynlp
urllib3
"""

# 파일 업데이트
with open("backend/requirements.txt", "w", encoding="utf-8") as f:
    f.write(req_content)

print("✅ 번역 엔진(DeepL)과 분석 도구들을 다시 목록에 넣었습니다!")
