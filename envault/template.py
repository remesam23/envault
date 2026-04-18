"""Template rendering: fill a .env.template with values from a vault profile."""
from __future__ import annotations
import re
from typing import Optional

MISSING_VAR_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class TemplateError(Exception):
    pass


def render_template(template: str, env: dict[str, str], strict: bool = True) -> str:
    """Replace ${VAR} placeholders in *template* with values from *env*.

    If *strict* is True (default) a TemplateError is raised for any
    placeholder whose key is absent from *env*.  Otherwise the placeholder
    is left as-is.
    """
    missing: list[str] = []

    def replacer(m: re.Match) -> str:
        key = m.group(1)
        if key in env:
            return env[key]
        if strict:
            missing.append(key)
            return m.group(0)
        return m.group(0)

    result = MISSING_VAR_RE.sub(replacer, template)
    if missing:
        raise TemplateError(
            f"Template references undefined variables: {', '.join(sorted(missing))}"
        )
    return result


def list_placeholders(template: str) -> list[str]:
    """Return sorted unique placeholder names found in *template*."""
    return sorted(set(MISSING_VAR_RE.findall(template)))


def render_file(
    template_path: str,
    env: dict[str, str],
    output_path: Optional[str] = None,
    strict: bool = True,
) -> str:
    """Read a template file, render it, optionally write output, return rendered text."""
    with open(template_path, "r", encoding="utf-8") as fh:
        template = fh.read()
    rendered = render_template(template, env, strict=strict)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(rendered)
    return rendered
