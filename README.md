# DocFlow

DocFlow는 교사용 제출물 문서 변환 및 검토 흐름을 돕기 위한 데스크톱 앱입니다.
현재 버전에서는 TXT와 Markdown 문서를 앱 내부에서 읽고, DOCX/XLSX/PPTX/HWPX 문서를 Markdown으로 변환해 확인하거나 저장하는 기본 구조를 제공합니다.

## MVP 범위

현재 버전은 제출물 문서를 탐색하고 읽는 데스크톱 리더기입니다.
TXT/Markdown은 그대로 읽고, DOCX는 문단/제목/표 구조를, XLSX는 시트/표 구조를, PPTX는 슬라이드별 텍스트 구조를, HWPX는 문단/표 구조를 Markdown으로 변환해 앱 안에서 확인하거나 Markdown 파일로 저장하는 흐름에 초점을 둡니다.

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

## 시연 흐름

DocFlow는 완전한 레이아웃 복원기가 아니라, 교사가 제출물 내용을 빠르게 확인하고 Markdown으로 정리하기 위한 검토 도구입니다.

1. `python main.py`로 앱을 실행합니다.
2. `입력 폴더 선택`으로 제출물이 들어 있는 폴더를 선택합니다.
3. 왼쪽 파일 목록에서 문서를 선택해 오른쪽 리더에서 미리보기합니다.
4. 필요하면 렌더링 보기와 원문 보기를 전환해 변환 결과를 확인합니다.
5. `출력 폴더 선택`으로 Markdown 저장 위치를 지정합니다.
6. `전체 Markdown 저장`을 실행해 모든 지원 문서를 `.md` 파일로 저장합니다.
7. 출력 폴더의 `export_report.csv`에서 성공/실패와 저장 경로를 확인합니다.

## 현재 지원 기능

- 입력 폴더 선택
- `.txt`, `.md`, `.markdown`, `.docx`, `.xlsx`, `.pptx`, `.hwpx` 파일 탐색 및 목록 표시
- TXT 파일 원문 보기
- Markdown 파일 렌더링 보기 및 원문 보기 전환
- DOCX 파일의 문단, Heading 1/2/3, 표를 Markdown으로 변환
- DOCX 변환 결과의 렌더링 보기 및 원문 보기 전환
- XLSX 파일의 각 worksheet를 Markdown 섹션과 표로 변환
- XLSX 변환 결과의 렌더링 보기 및 원문 보기 전환
- PPTX 파일의 각 슬라이드를 Markdown 섹션으로 변환하고 텍스트 박스/제목/본문 텍스트 추출
- PPTX 변환 결과의 렌더링 보기 및 원문 보기 전환
- HWPX 파일의 본문 section XML에서 문단과 가능한 표 구조를 Markdown으로 변환
- HWPX 변환 결과의 렌더링 보기 및 원문 보기 전환
- 선택 문서 또는 전체 문서를 UTF-8 Markdown 파일로 저장
- 저장 파일명은 원본 파일명을 기준으로 `.md` 확장자를 사용하며, 중복 시 새 이름으로 안전하게 저장
- 전체 저장 시 성공/실패 내역을 `export_report.csv`로 저장
- 리포트는 Excel에서 한글이 깨지지 않도록 UTF-8-sig 인코딩 사용
- 빈 폴더, 읽기 실패, 지원하지 않는 파일 형식에 대한 기본 예외 처리
- 하단 상태 로그 표시
- 폴더 스캔, 텍스트 인코딩, Markdown 렌더링, DOCX/XLSX/PPTX/HWPX 변환, Markdown 저장/리포트에 대한 pytest 테스트

## 아직 지원하지 않는 기능

- DOCX의 복잡한 레이아웃, 이미지, 주석, 머리글/바닥글 복원
- XLSX의 스타일, 수식 계산, 병합 셀 완전 복원
- PPTX의 디자인, 이미지, 애니메이션, 배치 완전 복원
- HWPX의 완전한 레이아웃, 스타일, 이미지 복원
- 문서 자동 검토 및 채점

## 다음 예정 기능

- 변환 대상 문서 형식 검토 및 변환 인터페이스 확장
- 저장 결과 파일 열기 동선 추가
- 교사용 검토 체크리스트 및 간단한 피드백 기록 기능
- 문서 읽기 실패 원인 안내 개선
