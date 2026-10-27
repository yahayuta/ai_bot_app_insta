import pytest

import main

PATHS = [
    ("get", "/stability_post_insta"),
    ("get", "/openai_post_insta"),
    ("get", "/imagen_post_insta"),
    ("get", "/test_prompt_strategies"),
    ("get", "/prompt_performance"),
    ("post", "/reset_prompt_performance"),
]


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("JOB_TOKEN", "job-test-token")
    return main.app.test_client()


@pytest.mark.parametrize("method,path", PATHS)
def test_requires_token(client, method, path):
    call = getattr(client, method)
    assert call(path).status_code == 403
    assert call(path, headers={"X-Job-Token": "wrong"}).status_code == 403


@pytest.mark.parametrize("method,path", PATHS)
def test_rejects_when_token_not_configured(client, monkeypatch, method, path):
    monkeypatch.setenv("JOB_TOKEN", "")
    assert getattr(client, method)(path, headers={"X-Job-Token": ""}).status_code == 403


def test_valid_token_reaches_endpoint(client):
    r = client.get("/prompt_performance", headers={"X-Job-Token": "job-test-token"})
    assert r.status_code == 200
    assert "performance" in r.get_json()
