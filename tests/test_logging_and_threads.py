import main

SECRET = "IGAAsecret-token-value"
THREADS_SECRET = "THAAsecret-threads-value"


class Res:
    def __init__(self, status=200, body=None):
        self.status_code = status
        self._body = body or {"id": "1", "status_code": "FINISHED", "status": "FINISHED"}
        self.text = str(self._body)

    def json(self):
        return self._body


def test_redact_masks_only_the_token():
    assert main.redact({"access_token": SECRET, "caption": "hi"}) == {"access_token": "***", "caption": "hi"}


def test_instagram_post_does_not_log_token(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(main, "PAGE_ACCESS_TOKEN", SECRET)
    monkeypatch.setattr(main.requests, "post", lambda url, **kw: calls.append(kw) or Res())
    monkeypatch.setattr(main.requests, "get", lambda url, **kw: calls.append(kw) or Res())
    monkeypatch.setattr(main.time, "sleep", lambda s: None)
    main.exec_instagram_post("https://example.com/a.png", "caption")
    out = capsys.readouterr().out
    assert SECRET not in out
    assert any(c.get("params", {}).get("access_token") == SECRET for c in calls)  # still sent to the API


def test_threads_post_does_not_log_token(monkeypatch, capsys):
    monkeypatch.setattr(main, "THREADS_API_TOKEN", THREADS_SECRET)
    monkeypatch.setattr(main.requests, "post", lambda url, **kw: Res())
    monkeypatch.setattr(main.requests, "get", lambda url, **kw: Res())
    monkeypatch.setattr(main.time, "sleep", lambda s: None)
    main.exec_threads_post("https://example.com/a.png", "caption")
    assert THREADS_SECRET not in capsys.readouterr().out


def test_threads_failure_does_not_raise(monkeypatch, capsys):
    def boom(*a, **k):
        raise Exception("Error validating access token: Session has expired")

    monkeypatch.setattr(main, "exec_threads_post", boom)
    assert main.post_to_threads_safely("https://example.com/a.png", "caption") is False
    assert "Threads post failed" in capsys.readouterr().out


def test_threads_success_returns_true(monkeypatch):
    monkeypatch.setattr(main, "exec_threads_post", lambda *a, **k: None)
    assert main.post_to_threads_safely("https://example.com/a.png", "caption") is True
