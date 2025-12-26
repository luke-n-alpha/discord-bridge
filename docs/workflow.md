# Discord Summarizer 작업 플로우 (Alpha-Codex System)

## 1. 작업 모델: Manager & Worker
이 프로젝트는 **Alpha (Manager/Supervisor)**와 **Codex (Worker/Builder)**의 협업 모델로 진행됩니다.

### 🤖 Alpha (Caret) - Manager
- **역할**: 프로젝트 관리, 환경 설정, 아키텍처 설계, 작업 지시서 작성, 코드 리뷰.
- **책임**:
    - 프로젝트의 올바른 방향성 유지.
    - 실행 환경(OS, 의존성)의 무결성 보장.
    - Worker가 작업할 수 있는 명확한 문서(`Task Spec`) 제공.
    - 결과물 통합 및 품질 검증.

### 👷 Codex - Worker
- **역할**: 기능 구현, 버그 수정, 단위 테스트 작성.
- **책임**:
    - 할당된 `Task Spec`을 정확히 구현.
    - 기존 코드를 깨뜨리지 않는 범위 내에서 작업.
    - 작업 완료 후 변경 사항과 테스트 결과를 리포트.

---

## 2. 작업 프로세스 (The Loop)

### Step 1: 계획 및 지시 (Alpha)
1. Alpha는 현재 필요한 작업을 분석합니다.
2. `work-logs/luke/discord-summarizer/01.todo` 폴더에 작업 지시서를 작성합니다.
3. 파일명은 `YYYYMMDD-%2d-{주제}.md` 규칙을 따릅니다.
4. 지시서에는 **목표, 수정할 파일 범위, 요구 사항, 검증 방법**이 명시됩니다.

### Step 2: 작업 수행 (Codex)
1. 사용자는 Codex 세션에 `Task-XXX.md` 내용을 전달하거나 파일을 읽게 합니다.
2. Codex는 지시서에 따라 코드를 작성하고 수정합니다.
3. Codex는 로컬 테스트를 수행하여 기능 동작을 확인합니다.

### Step 3: 리뷰 및 통합 (Alpha)
1. 사용자는 Alpha에게 작업 완료를 알립니다.
2. Alpha는 변경된 파일과 실행 결과를 확인(Review)합니다.
3. 문제가 없다면 다음 태스크로 넘어가고, 문제가 있다면 수정 지시를 내립니다.

---

## 3. 문서 표준

### 작업 지시서 템플릿 (`work-logs/luke/discord-summarizer/01.todo`)
```markdown
# Task-XXX: [작업명]

## 1. 개요
- **목표**: (무엇을 달성해야 하는가)
- **배경**: (왜 이 작업이 필요한가)

## 2. 상세 요구사항
- [ ] 기능 A 구현
- [ ] 버그 B 수정
- [ ] 조건 C 만족

## 3. 작업 범위
- 수정 파일: `src/main.rs`, `frontend/App.tsx`
- 참고 문서: `docs/architecture.md`

## 4. 검증 방법
- `npm run test` 통과
- 스크린샷 첨부 등
