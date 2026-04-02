from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_FILE = REPO_ROOT / "index.html"
SKIP_DIRS = {".git", ".github", "__pycache__", "docs", "scripts"}
SKIP_FILES = {"index.html", ".DS_Store", ".gitignore"}


def iter_dirs() -> list[Path]:
    dirs: list[Path] = [Path(".")]
    for path in sorted(REPO_ROOT.rglob("*")):
        if not path.is_dir():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(REPO_ROOT).parts):
            continue
        dirs.append(path.relative_to(REPO_ROOT))
    return dirs


def files_in_dir(rel_dir: Path) -> list[Path]:
    directory = REPO_ROOT / rel_dir
    files: list[Path] = []
    for child in sorted(directory.iterdir()):
        if child.name in SKIP_DIRS or child.name in SKIP_FILES:
            continue
        if child.is_file():
            files.append(child.relative_to(REPO_ROOT))
    return files


def dir_href(rel_dir: Path) -> str:
    if rel_dir == Path("."):
        return "/"
    return f"/{rel_dir.as_posix()}/"


def file_href(rel_file: Path) -> str:
    return f"/{rel_file.as_posix()}"


def render_list(items: list[tuple[str, str]]) -> str:
    if not items:
        return "<p class=\"empty\">None</p>"
    lines = ["<ul>"]
    for href, label in items:
        lines.append(
            f'  <li><a href="{escape(href, quote=True)}">{escape(label)}</a></li>'
        )
    lines.append("</ul>")
    return "\n".join(lines)


def build_html() -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    sections: list[str] = []

    root_files = [(file_href(path), path.name) for path in files_in_dir(Path("."))]
    sections.append("<section>")
    sections.append("<h2>Root Files</h2>")
    sections.append(render_list(root_files))
    sections.append("</section>")

    directories = [rel_dir for rel_dir in iter_dirs() if rel_dir != Path(".")]
    directory_links = [(dir_href(rel_dir), rel_dir.as_posix()) for rel_dir in directories]
    sections.append("<section>")
    sections.append("<h2>Directories</h2>")
    sections.append(render_list(directory_links))
    sections.append("</section>")

    for rel_dir in directories:
        section_files = [
            (file_href(path), path.name)
            for path in files_in_dir(rel_dir)
        ]
        sections.append("<section>")
        sections.append(
            f"<h2>{escape(rel_dir.as_posix())}</h2>"
        )
        sections.append(f'<p><a href="{escape(dir_href(rel_dir), quote=True)}">{escape(dir_href(rel_dir))}</a></p>')
        sections.append(render_list(section_files))
        sections.append("</section>")

    body = "\n".join(sections)
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Assets Index</title>
    <style>
      :root {{
        color-scheme: light;
      }}
      body {{
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        margin: 40px auto;
        max-width: 900px;
        padding: 0 20px 40px;
        line-height: 1.5;
        color: #111827;
      }}
      h1, h2 {{
        line-height: 1.2;
      }}
      section {{
        margin-top: 28px;
      }}
      ul {{
        padding-left: 20px;
      }}
      a {{
        color: #0f766e;
        text-decoration: none;
      }}
      a:hover {{
        text-decoration: underline;
      }}
      .meta, .empty {{
        color: #4b5563;
      }}
    </style>
  </head>
  <body>
    <h1>Assets Index</h1>
    <p class="meta">Static file listing for <code>app.ashish.me</code>.</p>
    <p class="meta">Generated {escape(generated_at)}.</p>
    {body}
  </body>
</html>
"""


def main() -> None:
    OUTPUT_FILE.write_text(build_html(), encoding="utf-8")


if __name__ == "__main__":
    main()
