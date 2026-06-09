# DocFlow

DocFlow는 교사용 제출물 문서 변환 및 검토 흐름을 돕기 위한 데스크톱 앱입니다.
현재 1차 MVP에서는 고급 문서 변환 기능을 구현하지 않고, TXT와 Markdown 문서를 앱 내부에서 읽고 확인하는 기본 구조를 제공합니다.

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

## 현재 지원 기능

- 입력 폴더 선택
- `.txt`, `.md`, `.markdown` 파일 탐색 및 목록 표시
- TXT 파일 원문 보기
- Markdown 파일 렌더링 보기 및 원문 보기 전환
- 빈 폴더, 읽기 실패, 지원하지 않는 파일 형식에 대한 기본 예외 처리
- 하단 상태 로그 표시

## 아직 지원하지 않는 기능

- HWPX, DOCX, PPTX, XLSX 변환
- 문서 자동 검토 및 채점
- 결과 내보내기
