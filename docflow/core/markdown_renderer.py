from __future__ import annotations

from docflow.core.document_model import DocumentLoadError


def render_markdown(source: str) -> str:
    """Convert Markdown text into a small HTML document for QTextBrowser."""
    try:
        import markdown
    except ModuleNotFoundError as exc:
        raise DocumentLoadError("Markdown 패키지가 설치되어 있지 않습니다.") from exc

    body = markdown.markdown(
        source,
        extensions=["extra", "sane_lists", "nl2br"],
        output_format="html5",
    )
    return f"""
    <!doctype html>
    <html>
      <head>
        <meta charset="utf-8">
        <style>
          body {{
            color: #20262b;
            font-family: "Segoe UI", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
            font-size: 15px;
            line-height: 1.6;
            margin: 18px;
          }}
          h1, h2, h3 {{
            color: #163849;
            margin-top: 1.1em;
          }}
          code {{
            background: #eef2f3;
            border-radius: 4px;
            padding: 2px 4px;
          }}
          pre {{
            background: #eef2f3;
            border: 1px solid #d6dcdf;
            border-radius: 6px;
            padding: 10px;
          }}
          blockquote {{
            border-left: 4px solid #78a9bd;
            color: #40515b;
            margin-left: 0;
            padding-left: 12px;
          }}
          table {{
            border-collapse: collapse;
          }}
          th, td {{
            border: 1px solid #cfd8dc;
            padding: 6px 8px;
          }}
        </style>
      </head>
      <body>{body}</body>
    </html>
    """
