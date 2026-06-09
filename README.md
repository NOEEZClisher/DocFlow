# DocFlow

DocFlow는 교사용 제출물 문서 변환 및 검토 흐름을 돕기 위한 데스크톱 앱입니다.
현재 1차 MVP에서는 고급 문서 변환 기능을 구현하지 않고, TXT와 Markdown 문서를 앱 내부에서 읽고 확인하는 기본 구조를 제공합니다.

## MVP 범위

현재 버전은 문서 변환 엔진이 아니라, 제출물 문서를 탐색하고 읽는 데스크톱 리더기입니다.
입력 폴더에서 텍스트 기반 문서만 찾아 목록화하고, 선택한 파일을 앱 안에서 확인하는 흐름을 안정화하는 데 초점을 둡니다.

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
- `.txt`, `.md`, `.markdown` 파일 탐색 및 목록 표시
- TXT 파일 원문 보기
- Markdown 파일 렌더링 보기 및 원문 보기 전환
- 빈 폴더, 읽기 실패, 지원하지 않는 파일 형식에 대한 기본 예외 처리
- 하단 상태 로그 표시
- 폴더 스캔, 텍스트 인코딩, Markdown 렌더링에 대한 pytest 테스트

## 아직 지원하지 않는 기능

- HWPX, DOCX, PPTX, XLSX 변환
- 문서 자동 검토 및 채점
- 결과 내보내기

## 다음 예정 기능

- 변환 대상 문서 형식 검토 및 변환 인터페이스 확장
- 변환 결과 미리보기와 저장 흐름 추가
- 교사용 검토 체크리스트 및 간단한 피드백 기록 기능
- 문서 읽기 실패 원인 안내 개선
