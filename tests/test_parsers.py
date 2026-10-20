from depfresh.parsers import (
    parse_package_json,
    parse_requirements,
    parse_pyproject,
    parse_cargo,
)


def test_package_json():
    text = '{"dependencies": {"react": "^18.0.0"}, "devDependencies": {"jest": "~29.0.0"}}'
    deps = parse_package_json(text)
    assert len(deps) == 2
    assert deps[0].name == "react" and deps[0].version == "18.0.0"
    assert deps[1].dev is True


def test_requirements():
    text = "requests==2.31.0\nflask>=2.0\n# comment\n-r other.txt\n"
    deps = parse_requirements(text)
    assert [d.name for d in deps] == ["requests", "flask"]
    assert deps[0].version == "2.31.0"


def test_pyproject_pep508():
    text = '''[project]
dependencies = ["requests>=2.0", "click"]
[project.optional-dependencies]
dev = ["pytest>=7"]
'''
    deps = parse_pyproject(text)
    names = [d.name for d in deps]
    assert "requests" in names and "click" in names and "pytest" in names


def test_pyproject_poetry():
    text = '''[tool.poetry.dependencies]
python = "^3.11"
requests = "^2.31"
[tool.poetry.dev-dependencies]
pytest = "^7.0"
'''
    deps = parse_pyproject(text)
    names = [d.name for d in deps]
    assert "requests" in names and "pytest" in names
    assert "python" not in names


def test_cargo():
    text = '''[dependencies]
serde = "1.0"
[dev-dependencies]
criterion = { version = "0.5", features = ["html_reports"] }
'''
    deps = parse_cargo(text)
    assert len(deps) == 2
    assert deps[1].dev is True
    assert deps[1].version == "0.5"
