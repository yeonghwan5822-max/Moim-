# User Guide: Moim Translator Streamlit Demo

이 문서는 '대학생 기독교 공동체 AI 번역 시스템'의 통합 데모(Streamlit App) 실행 방법을 안내합니다.

## 시스템 요구사항
- **OS**: macOS (User Environment)
- **Python**: 3.9+ 
- **Browser**: Chrome (for Crawler & UI)

## 1. 터미널 열기 및 경로 이동
터미널을 열고 프로젝트의 `backend` 디렉토리로 이동합니다.

```bash
cd "/Users/mac/Desktop/moim 번역기 프로젝트/backend"
```

## 2. 가상환경 활성화
Python 가상환경을 활성화하여 필요한 라이브러리를 로드합니다.

```bash
source .venv/bin/activate
```
*(성공 시 터미널 프롬프트 앞에 `(.venv)`가 표시됩니다)*

## 3. 앱 실행
Streamlit 앱을 실행합니다.

```bash
streamlit run streamlit_app.py
```

## 4. 접속 방법
명령어를 실행하면 자동으로 브라우저가 열립니다. 만약 열리지 않는다면 아래 주소를 주소창에 입력하세요:

- **Local URL**: `http://localhost:8501`
- **Network URL**: `http://[Your IP]:8501` (같은 와이파이 내 핸드폰 접속 가능)

## 5. 주요 기능 사용법

### 1) Crawler 탭
- **Board URL**: 크롤링할 대상 URL을 입력합니다. (기본값 설정됨)
- **Keyword**: '실습', '공지' 등 수집하고 싶은 단어를 입력합니다.
- **Start**: 크롤링이 시작되면 브라우저가 백그라운드에서 실행되며 데이터를 수집합니다.

### 2) OOV Detector 탭
- **Input Source**: 'Crawled Data'를 선택하면 방금 수집한 데이터를 분석합니다.
- **Run**: 버튼을 누르면 `soynlp`가 단어를 추출하고, **성경 용어 및 불용어를 자동으로 필터링**한 결과를 보여줍니다.

### 3) Translator 탭
- 번역할 문장을 입력하고 **Translate**를 누릅니다.
- **RAG Context**: 입력한 문장과 유사한 과거 데이터가 있다면 왼쪽에 표시됩니다.
- **Result**: 용어집(Glossary)이 적용된 번역 결과를 확인합니다.

---
**Q: 실행 중 에러가 발생하나요?**
터미널에서 `Ctrl+C`를 눌러 앱을 종료한 뒤, 다시 실행해 보세요.
