"""Serve only generated public files; rebuild when authoring sources change."""

import functools
import http.server
import importlib
import threading

import build_site

OUT, ROOT = build_site.OUT, build_site.ROOT


def fingerprint() -> tuple:
    paths = list((ROOT / "docs").rglob("*.md")) + list((ROOT / "site").rglob("*"))
    paths += list((ROOT / "assets").rglob("*")) + list(ROOT.glob("*.md"))
    paths += [
        path
        for path in (ROOT / "examples").rglob("*")
        if path.suffix in {".py", ".md", ".json", ".sql", ".txt"}
        and "__pycache__" not in path.parts
    ]
    paths += list((ROOT / "scripts").rglob("*.py"))
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
                    "curriculum",
                    "asset_paths",
                    "site_output",
                    "diagrams.raster",
                    "diagrams.svg_canvas",
                    "curriculum_docs",
                    "diagrams.foundation_scenes",
                    "diagrams.agent_scenes",
                    "diagrams.architecture_scenes",
                    "diagrams.mcp_scenes",
                    "diagrams.skill_scenes",
                    "diagrams.governance_scenes",
                    "diagrams.multi_agent_scenes",
                    "diagrams.studio_scenes",
                    "diagrams.solution_scenes",
                    "diagrams.deep_scenes",
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
