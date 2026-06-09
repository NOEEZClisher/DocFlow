# DocFlow

DocFlow는 교사용 제출물 문서 변환 및 검토 흐름을 돕기 위한 데스크톱 앱입니다.
현재 버전에서는 TXT와 Markdown 문서를 앱 내부에서 읽고, DOCX/XLSX 문서를 Markdown으로 변환해 확인하거나 저장하는 기본 구조를 제공합니다.

## MVP 범위

현재 버전은 제출물 문서를 탐색하고 읽는 데스크톱 리더기입니다.
TXT/Markdown은 그대로 읽고, DOCX는 문단/제목/표 구조를, XLSX는 시트/표 구조를 Markdown으로 변환해 앱 안에서 확인하거나 Markdown 파일로 저장하는 흐름에 초점을 둡니다.

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Windows PowerShell에서는 가상환경 활성화 명령을 아래처럼 사용할 수 있습니다.

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## 테스트 실행

```bash
pytest
```

## 현재 지원 기능

- 입력 폴더 선택
- `.txt`, `.md`, `.markdown`, `.docx`, `.xlsx` 파일 탐색 및 목록 표시
- TXT 파일 원문 보기
- Markdown 파일 렌더링 보기 및 원문 보기 전환
- DOCX 파일의 문단, Heading 1/2/3, 표를 Markdown으로 변환
- DOCX 변환 결과의 렌더링 보기 및 원문 보기 전환
- XLSX 파일의 각 worksheet를 Markdown 섹션과 표로 변환
- XLSX 변환 결과의 렌더링 보기 및 원문 보기 전환
- 선택 문서 또는 전체 문서를 UTF-8 Markdown 파일로 저장
- 저장 파일명은 원본 파일명을 기준으로 `.md` 확장자를 사용하며, 중복 시 새 이름으로 안전하게 저장
- 빈 폴더, 읽기 실패, 지원하지 않는 파일 형식에 대한 기본 예외 처리
- 하단 상태 로그 표시
- 폴더 스캔, 텍스트 인코딩, Markdown 렌더링, DOCX/XLSX 변환, Markdown 저장에 대한 pytest 테스트

## 아직 지원하지 않는 기능

- HWPX, PPTX 변환
- DOCX의 복잡한 레이아웃, 이미지, 주석, 머리글/바닥글 복원
- XLSX의 스타일, 수식 계산, 병합 셀 완전 복원
- 문서 자동 검토 및 채점

## 다음 예정 기능

- 변환 대상 문서 형식 검토 및 변환 인터페이스 확장
- 저장 결과 상세 리포트와 파일 열기 동선 추가
- 교사용 검토 체크리스트 및 간단한 피드백 기록 기능
- 문서 읽기 실패 원인 안내 개선
