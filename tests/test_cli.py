"""Tests for the Hammy CLI."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from hammy.cli import app

runner = CliRunner()


class TestInit:
    def test_init_creates_config(self, tmp_path: Path):
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "hammy.yaml").exists()
        assert (tmp_path / "config" / "agents.yaml").exists()
        assert (tmp_path / ".hammyignore").exists()

    def test_init_doesnt_overwrite(self, tmp_path: Path):
        # First init
        runner.invoke(app, ["init", str(tmp_path)])
        # Write custom content
        (tmp_path / "hammy.yaml").write_text("custom: true")
        # Second init should not overwrite
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert "custom: true" in (tmp_path / "hammy.yaml").read_text()

    def test_init_creates_hammy_md(self, tmp_path: Path):
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        hammy_md = tmp_path / "HAMMY.md"
        assert hammy_md.exists()
        content = hammy_md.read_text()
        assert "find_usages" in content
        assert "impact_analysis" in content
        # Points users at referencing it from their own agent context files
        assert "HAMMY.md" in result.output

    def test_init_doesnt_overwrite_hammy_md(self, tmp_path: Path):
        runner.invoke(app, ["init", str(tmp_path)])
        (tmp_path / "HAMMY.md").write_text("customized")
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / "HAMMY.md").read_text() == "customized"

    def test_init_skips_skill_without_claude_dir(self, tmp_path: Path):
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert not (tmp_path / ".claude").exists()

    def test_init_installs_skill_with_flag(self, tmp_path: Path):
        result = runner.invoke(app, ["init", str(tmp_path), "--claude-skill"])
        assert result.exit_code == 0
        skill = tmp_path / ".claude" / "skills" / "hammy" / "SKILL.md"
        assert skill.exists()
        content = skill.read_text()
        assert content.startswith("---")
        assert "name: hammy" in content
        assert "HAMMY.md" in content

    def test_init_installs_skill_when_claude_dir_exists(self, tmp_path: Path):
        (tmp_path / ".claude").mkdir()
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert (tmp_path / ".claude" / "skills" / "hammy" / "SKILL.md").exists()

    def test_init_doesnt_overwrite_skill(self, tmp_path: Path):
        runner.invoke(app, ["init", str(tmp_path), "--claude-skill"])
        skill = tmp_path / ".claude" / "skills" / "hammy" / "SKILL.md"
        skill.write_text("customized")
        result = runner.invoke(app, ["init", str(tmp_path)])
        assert result.exit_code == 0
        assert skill.read_text() == "customized"


class TestIndex:
    def test_index_no_qdrant(self, tmp_path: Path):
        # Create some source files
        (tmp_path / "app.php").write_text("<?php class App {}")
        (tmp_path / "main.js").write_text("function main() {}")

        # Create minimal config
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "hammy.yaml").write_text(
            "project:\n  root: .\nparsing:\n  languages:\n    - php\n    - javascript\n"
        )

        result = runner.invoke(app, ["index", str(tmp_path), "--no-qdrant", "--no-commits"])
        assert result.exit_code == 0
        assert "Files processed" in result.output
        assert "2" in result.output  # 2 files


class TestStatus:
    def test_status_basic(self, tmp_path: Path):
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        (config_dir / "hammy.yaml").write_text(
            "project:\n  root: .\nparsing:\n  languages:\n    - php\n"
        )

        result = runner.invoke(app, ["status", str(tmp_path)])
        assert result.exit_code == 0
        assert "Project root" in result.output
