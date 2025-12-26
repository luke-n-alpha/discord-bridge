# 작업 계획: 프로젝트 컨텍스트 정리 및 환경 설정

## 1. 개요
- **목적**: AI 에이전트가 프로젝트의 구조, 실행 방법, 현재 이슈를 매번 다시 학습하지 않도록 `.caretrules/` 내에 영구적인 컨텍스트 파일을 생성함.
- **이후 목표**: 컨텍스트 확립 후, 현재 블로커인 리눅스 `webkit2gtk` 의존성 문제를 해결하고 Tauri 앱을 실행함.

## 2. 생성할 파일: `.caretrules/project_context.md`
이 파일에는 다음 내용이 포함됩니다:
- **Project Identity**: Discord Summarizer (Python + Tauri).
- **Directory Map**:
    - `bridge/`: Python 로직 (핵심).
    - `frontend/`: React UI.
    - `src-tauri/`: Rust 어댑터.
    - `scripts/`: 자동화 스크립트.
- **Critical Commands**:
    - Bootstrap: `./scripts/bootstrap.sh`
    - Run Tauri: `./scripts/dev_tauri.sh`
    - Run Python CLI: `python -m bridge.cli ...`
- **Current Context (Active Memory)**:
    - 상태: Python OK, Tauri 실행 실패.
    - 해결 과제: `webkit2gtk-4.0` 라이브러리 설치 필요.
- **Rules**:
    - 언어: 한국어/영어 병기 문서 유지.
    - 경로: 프로젝트 루트 `/var/home/luke/dev/discord-summarizer` 기준 작업.

## 3. 실행 단계
1. `.caretrules` 디렉토리 생성 (없을 시).
2. `project_context.md` 작성.
3. (승인 시) 리눅스 패키지 설치: `sudo dnf install webkit2gtk4.0-devel librsvg2-devel`.
4. Tauri 실행 확인.
