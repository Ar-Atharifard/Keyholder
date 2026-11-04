"""HTTP transport contracts for the extracted operator logic."""

from typing import Any

import pytest
from fastapi.testclient import TestClient

from keyholder import admin_operations
from tests.support import HEADERS, create


def operation(client: TestClient, operation_name: str, **args: Any) -> Any:
    response = client.post(
        "/admin/operations", headers=HEADERS, json={"operation": operation_name, "args": args}
    )
    assert response.status_code == 200, response.text
    return response.json()["result"]


def test_authentication_and_rejection_of_host_operations(client: TestClient) -> None:
    assert client.post("/admin/operations", json={"operation": "backends"}).status_code == 401
    for name in ("status", "backup", "system-metrics", "personal-dnstt", "exec"):
        response = client.post(
            "/admin/operations", headers=HEADERS, json={"operation": name, "args": {}}
        )
        assert response.status_code == 422


def test_http_operations_preserve_customer_identity_and_link(client: TestClient) -> None:
    result = create(client)
    customer = result["customer"]
    assert isinstance(customer, dict)
    cid = customer["id"]
    token = str(result["token"])
    assert operation(client, "show", customer=cid)["id"] == cid
    assert operation(client, "list", limit=20, offset=0)[0]["id"] == cid
    assert operation(client, "link", customer=cid)["token"] == token
    operation(client, "rename", customer=cid, name="Updated name")
    assert operation(client, "link", customer=cid)["subscription_url"] == result["subscription_url"]
    operation(client, "disable", customer=cid)
    assert client.get("/s/" + token).status_code == 404
    operation(client, "enable", customer=cid)
    assert client.get("/s/" + token).status_code == 200
    assert admin_operations.APPLICATION.get() is None


@pytest.mark.parametrize("name", ["revoke", "rotate-token"])
def test_destructive_operations_require_confirmation(client: TestClient, name: str) -> None:
    result = create(client)
    customer = result["customer"]
    assert isinstance(customer, dict)
    response = client.post(
        "/admin/operations",
        headers=HEADERS,
        json={"operation": name, "args": {"customer": customer["id"]}},
    )
    assert response.status_code == 422
    assert operation(client, "link", customer=customer["id"])["token"] == result["token"]


def test_operation_transport_from_async_panel_operation(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def panel(name: str, args: dict[str, Any]) -> Any:
        return admin_operations.api("GET", "/admin/backends")

    monkeypatch.setattr(admin_operations, "panel_operation", panel)
    assert operation(client, "users")[0]["id"] == "marzban-default"


def test_account_quota_updates_keep_credentials_and_usage(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    import httpx

    from keyholder.backends.marzban import MarzbanBackend

    account = {
        "username": "alice",
        "status": "active",
        "data_limit": 10 * 1024**3,
        "used_traffic": 1024,
        "expire": 1234,
        "proxies": {"vless": {"id": "private-credential"}},
        "inbounds": {"vless": ["A"]},
    }
    updates = []

    async def login(self: MarzbanBackend) -> None:
        self.token = "synthetic"

    async def request(
        self: MarzbanBackend, method: str, path: str, **kwargs: Any
    ) -> httpx.Response:
        if method == "PUT":
            updates.append(kwargs["json"])
            account.update(kwargs["json"])
        return httpx.Response(200, json=account)

    monkeypatch.setattr(MarzbanBackend, "login", login)
    monkeypatch.setattr(MarzbanBackend, "request", request)
    result = operation(client, "user-update", username="alice", quota_gb=30, days=0)
    assert updates == [{"data_limit": 30 * 1024**3, "expire": 0}]
    assert account["proxies"] == {"vless": {"id": "private-credential"}}
    assert result["used_traffic"] == 1024
    assert "private-credential" not in str(result)


@pytest.mark.parametrize("args", [{"quota_gb": -1}, {"days": -1}, {"confirmed": "false"}])
def test_invalid_arguments_never_reach_panel(
    client: TestClient, monkeypatch: pytest.MonkeyPatch, args: dict[str, Any]
) -> None:
    async def unexpected(*values: Any) -> Any:
        pytest.fail("Invalid arguments reached the panel")

    monkeypatch.setattr(admin_operations, "panel_operation", unexpected)
    response = client.post(
        "/admin/operations",
        headers=HEADERS,
        json={"operation": "user-update", "args": {"username": "alice", **args}},
    )
    assert response.status_code == 422
