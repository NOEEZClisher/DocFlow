from __future__ import annotations

from docflow.core.markdown_renderer import render_markdown


def test_render_markdown_converts_heading_paragraph_and_table() -> None:
    html = render_markdown(
        """
# 제출물 검토

학생 문서를 확인합니다.

| 항목 | 상태 |
| --- | --- |
| 초안 | 완료 |
""".strip()
    )

    assert "<h1>제출물 검토</h1>" in html
    assert "<p>학생 문서를 확인합니다.</p>" in html
    assert "<table>" in html
    assert "<th>항목</th>" in html
    assert "<td>완료</td>" in html
