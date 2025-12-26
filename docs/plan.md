# Discord Bridge 개발 계획 (TDD 우선)

## 목표와 우선순위
- 1순위: Google/OpenAI(API 호환) 기반 요약 → Markdown 생성.
- 2순위: SMTP로 리포트 전송(테스트 전송 + 실패 재시도).
- 3순위: Ollama(로컬) 연동.
- 공통: 전처리 → 요약 → 저장 → 발송까지 자동화. TDD로 진행.

## 단계별 계획
1. 구성/설정
   - .env 스키마 고정(.env.example 동기화). 필수/옵션 키 검증 유틸.
   - 출력/입력 경로, 스케줄, LLM, SMTP 섹션 분리.
   - TDD: 환경 검증 함수/클래스에 대한 단위 테스트 작성 후 구현.
2. LLM 프로바이더 추상화 (Google/OpenAI 우선)
   - 인터페이스: `SummarizerProvider.generate_summary(transcript, mode)` 등.
   - 구현: OpenAI 호환 클라이언트, Google Gemini(REST/SDK) 옵션화.
   - TDD: 모의 응답/스텁으로 요약 포맷/에러 처리 테스트.
3. 오케스트레이터 (CLI 우선)
   - 흐름: 입력 JSON 로드 → 전처리(기존 스크립트 호출 또는 직접) → 요약 호출 → Markdown 저장.
   - 옵션: FAQ/Help/ActionItems vs Q&A 모드.
   - TDD: 샘플 JSON으로 엔드투엔드 테스트(LLM 모의).
4. SMTP 발송
   - 설정: host/port/username/password/TLS, from/to(다중).
   - 기능: 테스트 전송, 본문 요약 포함 + MD 첨부, 재시도(backoff).
   - TDD: 모의 SMTP 서버 또는 smtplib mock으로 성공/실패 경로 테스트.
5. Ollama(로컬) 연동
   - 기존 summarize.py 로직을 프로바이더로 이동/호출.
   - 리소스 부족/에러 시 graceful fallback 처리.
   - TDD: 스텁으로 호출 경로만 검증.
6. 빌드/배포 준비
   - PyInstaller 스크립트(3 OS).
   - Tauri 프론트엔드: 설정/이메일/스케줄/로그 UI 골격, “env 내보내기”, “지금 실행”.
   - 이후 E2E(프론트→백엔드) 스냅샷/통합 테스트 추가.

## TDD 원칙 적용
- 각 단계 시작 전 실패하는 테스트 작성 → 구현 → 리팩터.
- 외부 서비스(LLM/SMTP)는 인터페이스화 후 mock/stub으로 테스트.
- 샘플 데이터(`samples/`)를 활용한 엔드투엔드/회귀 테스트 추가.

## E2E 시나리오 체크리스트
- CLI 기본 흐름: 샘플 입력 → 요약 → Markdown 저장 (모의 LLM 사용).
- 전처리 포함 흐름: `preprocess.py`/`preprocess_hourly.py` 적용 후 동일 경로 처리.
- 이메일 발송 흐름: mock SMTP로 성공/실패 및 재시도 경로 확인.
- 설정 검증 흐름: 필수 .env 누락 시 에러 메시지/로그 확인.
- UI 연계 흐름(가능 시): Tauri UI “지금 실행” → 번들 CLI 호출 → 결과/로그 확인.

## 보안/운영
- 비밀값은 .env 또는 OS 키체인, 커밋 금지(.gitignore 적용).
- 로그엔 비밀값 마스킹. 노출 시 즉시 재발급.

## 산출물
- 코드: 설정 로더, 프로바이더 인터페이스/구현, 오케스트레이터, SMTP 유틸.
- 문서: README, docs/manual.md, work-logs/luke/discord-summarizer/, docs/plan.md 동기화.
