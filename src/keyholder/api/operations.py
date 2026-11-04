"""Administrative account operations formerly invoked by an injected worker."""

import math
import re
from typing import Any, Literal, Self

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, model_validator

from keyholder import admin_operations
from keyholder.api.dependencies import admin

router = APIRouter(prefix="/admin", dependencies=[Depends(admin)])


class OperationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    operation: Literal[
        "backends",
        "backend-register",
        "users",
        "inbounds",
        "sync",
        "reconcile",
        "user-create",
        "user-update",
        "user-inbounds",
        "user-defaults",
        "user-usage",
        "user-reset-usage",
        "list",
        "create",
        "link",
        "configs",
        "config",
        "show",
        "customer-update",
        "check",
        "remap",
        "rotate-token",
        "revoke",
        "enable",
        "disable",
        "rename",
        "profiles",
        "billing-purchase-create",
        "billing-purchase-list",
        "billing-purchase-show",
        "billing-purchase-cancel",
        "billing-payment-create",
        "billing-payment-list",
        "billing-payment-show",
        "billing-payment-confirm",
        "billing-payment-void",
        "billing-payment-refund",
        "billing-payment-allocate",
        "billing-payment-allocations",
        "billing-payment-refunds",
        "billing-payment-unallocate",
        "billing-referral-create",
        "billing-referral-list",
        "billing-gift-create",
        "billing-gift-list",
        "billing-gift-reverse",
        "billing-receipt-upload",
        "billing-receipt-list",
        "billing-receipt-download",
        "billing-receipt-keep",
        "billing-receipt-release",
        "billing-storage-status",
        "billing-storage-reconcile",
        "billing-storage-reservations",
        "billing-storage-cleanup",
        "billing-storage-release-reservation",
        "billing-billing-balances",
        "billing-billing-actions",
    ]
    args: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_arguments(self) -> Self:
        args = self.args
        for flag in ("confirmed", "execute", "pressure"):
            if flag in args and type(args[flag]) is not bool:
                raise ValueError("Flags must be JSON booleans")
        if "backend_id" in args and (
            not isinstance(args["backend_id"], str)
            or not re.fullmatch(r"[a-zA-Z0-9_-]{1,64}", args["backend_id"])
        ):
            raise ValueError("Invalid backend ID")
        if self.operation == "list":
            args.setdefault("limit", 100)
            args.setdefault("offset", 0)
        for key, lower, upper in (("limit", 1, 100), ("offset", 0, 2**31), ("days", 0, 36500)):
            value = args.get(key)
            if value is not None and (type(value) is not int or not lower <= value <= upper):
                raise ValueError("Invalid numeric argument")
        quota = args.get("quota_gb")
        if quota is not None and (
            type(quota) not in (float, int) or not math.isfinite(quota) or quota < 0
        ):
            raise ValueError("Invalid quota")
        if self.operation.startswith("user-") and args.get("username") is not None:
            if not isinstance(args["username"], str) or not re.fullmatch(
                r"[A-Za-z0-9_]{3,32}", args["username"]
            ):
                raise ValueError("Invalid username")
        return self


@router.post("/operations", operation_id="admin_operation_v1")
def execute(body: OperationRequest, request: Request) -> dict[str, Any]:
    token = admin_operations.APPLICATION.set(request.app)
    try:
        return {"ok": True, "result": admin_operations.execute(body.operation, body.args)}
    except admin_operations.OperatorError as error:
        raise HTTPException(error.status or 422, str(error)) from None
    except (ValueError, KeyError, TypeError):
        raise HTTPException(422, "Invalid operation or arguments") from None
    finally:
        admin_operations.APPLICATION.reset(token)
