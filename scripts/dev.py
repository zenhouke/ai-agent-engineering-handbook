"""Serve only generated public files; rebuild when authoring sources change."""

import functools
import http.server
import importlib
import threading

import build_site

OUT, ROOT = build_site.OUT, build_site.ROOT


def fingerprint() -> tuple:
    paths = list((ROOT / "docs").rglob("*.md")) + list((ROOT / "site").rglob("*"))
    paths += (
        list((ROOT / "assets").rglob("*"))
        + list(ROOT.glob("*.md"))
        + list(ROOT.glob("*.svg"))
    )
    paths += [
        path
        for path in (ROOT / "examples").rglob("*")
        if path.suffix in {".py", ".md", ".json", ".sql", ".txt"}
        and "__pycache__" not in path.parts
    ]
    paths += list((ROOT / "scripts").glob("*.py"))
    return tuple(
        (str(path), path.stat().st_mtime_ns) for path in sorted(paths) if path.is_file()
    )


def watch(stop: threading.Event) -> None:
    previous = fingerprint()
    while not stop.wait(1):
        current = fingerprint()
        if current != previous:
            try:
                # Reload generators in dependency order: a long-running preview
                # must not regenerate pages with an older lesson/table renderer.
                for name in (
                    "svg_canvas",
                    "curriculum",
                    "curriculum_docs",
                    "foundation_scenes",
                    "agent_scenes",
                    "architecture_scenes",
                    "mcp_scenes",
                    "skill_scenes",
                    "governance_scenes",
                    "multi_agent_scenes",
                    "studio_scenes",
                    "solution_scenes",
                    "deep_scenes",
                    "visual_lessons",
                    "site_navigation",
                    "build_site",
                ):
                    importlib.reload(importlib.import_module(name))
                build_site.build()
                previous = current
            except (OSError, ValueError, SyntaxError, ImportError) as error:
                print(f"Build failed; keeping previous pages: {error}", flush=True)


if __name__ == "__main__":
    build_site.build()
    stop = threading.Event()
    watcher = threading.Thread(target=watch, args=(stop,), daemon=True)
    watcher.start()
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(OUT)
    )
    try:
        with http.server.ThreadingHTTPServer(("0.0.0.0", 32140), handler) as server:
            server.serve_forever()
    finally:
        stop.set()
        watcher.join(timeout=3)
