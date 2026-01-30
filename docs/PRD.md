# Product Requirements Document (PRD)

## Project Name
University Student Christian Community AI Translation System

## Background
- **Problem**: General AI translators fail due to **Domain Shift** and **OOV (Out-of-Vocabulary)** issues in this specific community.
- **Contexts**:
    1.  **Classical**: Biblical terms mixed with daily language.
    2.  **University Slang**: Abbreviations, new words.
    3.  **Practical**: Work/Service support terms.

## Core Goals
- **Immediate (1 Week PoC)**:
    -   Build an automated **OOV Detection Program** (Unsupervised Learning).
    -   Crawl 'ebc blue' community site (Hybrid Selenium + Scrapy).
- **Long-term (4 Months)**:
    -   Glossary integration with Enterprise Translation APIs.
    -   RAG (Retrieval-Augmented Generation) implementation.
    -   Voice data collection (Whisper STT).

## Technical Requirements (Functional)
1.  **OOV Detection Module**:
    -   Algorithm: `soynlp` (Cohesion Score + Branching Entropy).
    -   Filtering: TF-IDF for domain specificity verification.
    -   Output: Top 20 new words/week.
2.  **Crawling Engine**:
    -   Hybrid: Selenium (Login, iframes) + Scrapy (Bulk).
    -   Handling: Dynamic loading, anti-bot measures.
3.  **Translation API**:
    -   Hybrid: Reference RAG DB first, then external API (DeepL/Google) with Glossary.

## Technical Requirements (Non-Functional)
-   **Privacy**: PIPA compliance (Encryption, access control, deletion).
-   **Security**: Local processing where possible (e.g., Whisper).

## Roadmap
-   **Phase 1 (Month 1)**: Corpus construction, OOV mining (Target of this task).
-   **Phase 2 (Month 2)**: Hybrid Translation Architecture (Glossary + RAG).
-   **Phase 3 (Month 3)**: Beta Testing (Field usage).
-   **Phase 4 (Month 4)**: Optimization & Mobile Web.

## References
-   soynlp, TF-IDF, Selenium, Scrapy, RAG vs Fine-tuning.
