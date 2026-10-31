"""Workspace-confined discovery for local XML test reports."""
from pathlib import Path


MAX_REPORTS = 100


class ReportNotFoundError(FileNotFoundError):
    """Raised when a report is missing, unsafe, or outside the workspace."""


class ReportCatalog:
    """Find XML reports beneath one explicitly configured workspace root."""

    def __init__(self, workspace: Path, *, max_reports: int = MAX_REPORTS):
        if max_reports < 1:
            raise ValueError("max_reports must be positive")
        self.root = workspace.expanduser().resolve(strict=True)
        if not self.root.is_dir():
            raise ValueError("Workspace root must be a directory")
        self.max_reports = max_reports

    def list_reports(self) -> list[str]:
        """Return sorted relative report paths, bounded to ``max_reports``."""
        reports = []
        for candidate in self.root.rglob("*.xml"):
            if candidate.is_symlink() or not candidate.is_file():
                continue
            reports.append(candidate.relative_to(self.root).as_posix())
            if len(reports) > self.max_reports:
                raise ValueError(f"Workspace contains more than {self.max_reports} XML reports")
        return sorted(reports)

    def resolve_report(self, relative_path: str) -> Path:
        """Resolve an XML report while refusing traversal and symlink paths."""
        requested = Path(relative_path)
        if requested.is_absolute() or requested.suffix.lower() != ".xml":
            raise ReportNotFoundError("Report path must be a relative .xml file")
        candidate = self.root / requested
        if any(part == ".." for part in requested.parts):
            raise ReportNotFoundError("Report path cannot traverse outside the workspace")
        current = self.root
        for part in requested.parts:
            current = current / part
            if current.is_symlink():
                raise ReportNotFoundError("Symlink report paths are not allowed")
        try:
            resolved = candidate.resolve(strict=True)
        except (FileNotFoundError, OSError) as exc:
            raise ReportNotFoundError("Report does not exist") from exc
        if self.root not in resolved.parents or not resolved.is_file():
            raise ReportNotFoundError("Report must be a file inside the workspace")
        return resolved
