from pathlib import Path

import pytest

from testlens.catalog import ReportCatalog, ReportNotFoundError


def test_catalog_lists_relative_xml_reports(tmp_path: Path):
    (tmp_path / "reports").mkdir()
    (tmp_path / "reports" / "junit.xml").write_text("<testsuite />")
    (tmp_path / "notes.txt").write_text("not a report")
    catalog = ReportCatalog(tmp_path)

    assert catalog.list_reports() == ["reports/junit.xml"]
    assert catalog.resolve_report("reports/junit.xml").name == "junit.xml"


@pytest.mark.parametrize("name", ["../outside.xml", "/tmp/outside.xml", "notes.txt"])
def test_catalog_rejects_unsafe_paths(tmp_path: Path, name: str):
    catalog = ReportCatalog(tmp_path)

    with pytest.raises(ReportNotFoundError):
        catalog.resolve_report(name)


def test_catalog_rejects_symlink_reports(tmp_path: Path):
    outside = tmp_path.parent / f"{tmp_path.name}-outside.xml"
    outside.write_text("<testsuite />")
    (tmp_path / "linked.xml").symlink_to(outside)

    catalog = ReportCatalog(tmp_path)
    with pytest.raises(ReportNotFoundError, match="Symlink"):
        catalog.resolve_report("linked.xml")
    assert catalog.list_reports() == []


def test_catalog_caps_discovered_reports(tmp_path: Path):
    (tmp_path / "a.xml").write_text("<testsuite />")
    (tmp_path / "b.xml").write_text("<testsuite />")
    catalog = ReportCatalog(tmp_path, max_reports=1)

    with pytest.raises(ValueError, match="more than 1"):
        catalog.list_reports()
