# SKILL: Community-Specific AI Translator Builder

## 1. 개요
대학생 기독교 공동체만의 특수 용어(성경, 은어, 실습 용어)를 처리하는 맞춤형 번역 시스템 구축 스킬.

## 2. 핵심 작업 흐름 (MASTER)
1.  **Manual Run-through**
    *   `soynlp`를 사용하여 'ebc blue' 텍스트 샘플에서 신조어를 추출하는 과정을 시뮬레이션.
    *   입력: `references/corpus_sample.txt`
    *   실행: `python scripts/oov_detector.py`
2.  **Analyze**
    *   추출된 단어 중 TF-IDF 점수(혹은 복합 점수)가 높은 '공동체 전용 용어' 선별.
    *   결과 확인: 콘솔 출력 및 `backend/data/oov_candidates.json` (예정)
3.  **Systematize**
    *   `scripts/oov_detector.py`: 미등록 단어 탐지 자동화.
    *   `scripts/crawler.py`: Selenium + Scrapy 하이브리드 수집기.
    *   `scripts/translator_engine.py`: RAG 기반 DeepL 번역기.
4.  **Test**
    *   Whisper(예정)로 변환된 텍스트가 용어집(`references/glossary.json`)을 거쳐 정확히 번역되는지 검증.

## 3. 기술 스택 및 제약 사항
- **NLP:** soynlp (Cohesion, Branching Entropy 사용)
- **Data Collection:** Hybrid Crawler (Selenium + Scrapy)
- **STT:** OpenAI Whisper (로컬 실행 모드 권장)
- **Translation:** DeepL API + RAG (ChromaDB + SentenceTransformers)
- **Security:** PIPA 준수 (음성 데이터 처리 후 즉시 삭제)

## 4. 디렉토리 구조
```text
backend/
├── scripts/
│   ├── oov_detector.py    # soynlp 단어 추출
│   ├── crawler.py         # 하이브리드 크롤러
│   └── translator_engine.py # RAG 번역 엔진
├── references/
│   ├── glossary.json      # 용어 사전
│   └── corpus_sample.txt  # 샘플 텍스트
└── skills/
    └── SKILL.md           # 본 가이드라인
```
