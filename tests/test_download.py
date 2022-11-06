# SPDX-FileCopyrightText: 2019 Free Software Foundation Europe e.V. <https://fsfe.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

"""All tests for reuse.download"""

import urllib.request
from pathlib import Path
from urllib.error import URLError

import pytest

from reuse.download import download_license, put_license_in_file


class MockResponse:
    """Super simple mocked version of Response."""

    def __init__(self, text=None, status_code=None):
        self.text = text
        self.status_code = status_code

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        return False

    def read(self):
        return self.text.encode("utf-8")

    def getcode(self):
        return self.status_code


def test_download(monkeypatch):
    """A straightforward test: Request license text, get license text."""
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda _: MockResponse("hello", 200)
    )
    result = download_license("0BSD")
    assert result == "hello"


def test_download_404(monkeypatch):
    """If the server returns a 404, there is no license text."""
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda _: MockResponse(status_code=404)
    )
    with pytest.raises(URLError):
        download_license("does-not-exist")


def test_download_exception(monkeypatch):
    """If urllib raises an exception itself, that exception is not escaped."""

    def raise_exception(_):
        raise URLError("test")

    monkeypatch.setattr(urllib.request, "urlopen", raise_exception)
    with pytest.raises(URLError):
        download_license("hello world")


def test_put_simple(fake_repository, monkeypatch):
    """Straightforward test."""
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda _: MockResponse("hello\n", 200)
    )
    put_license_in_file("0BSD", "LICENSES/0BSD.txt")

    assert (fake_repository / "LICENSES/0BSD.txt").read_text() == "hello\n"


def test_put_file_exists(fake_repository, monkeypatch):
    """The to-be-downloaded file already exists."""
    # pylint: disable=unused-argument
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda _: MockResponse("hello\n", 200)
    )

    with pytest.raises(FileExistsError) as exc_info:
        put_license_in_file("GPL-3.0-or-later", "LICENSES/GPL-3.0-or-later.txt")
    assert Path(exc_info.value.filename).name == "GPL-3.0-or-later.txt"


def test_put_request_exception(fake_repository, monkeypatch):
    """There was an error while downloading the license file."""
    # pylint: disable=unused-argument
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda _: MockResponse(status_code=404)
    )

    with pytest.raises(URLError):
        put_license_in_file("0BSD", "LICENSES/0BSD.txt")


def test_put_empty_dir(empty_directory, monkeypatch):
    """Create a LICENSES/ directory if one does not yet exist."""
    monkeypatch.setattr(
        urllib.request, "urlopen", lambda _: MockResponse("hello\n", 200)
    )
    put_license_in_file("0BSD", "LICENSES/0BSD.txt")

    assert (empty_directory / "LICENSES").exists()
    assert (empty_directory / "LICENSES/0BSD.txt").read_text() == "hello\n"
