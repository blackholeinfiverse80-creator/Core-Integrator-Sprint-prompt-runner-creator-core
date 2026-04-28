"""Reliable instruction publisher for Prompt Runner.

This module provides secure delivery of generated instructions to downstream
systems over HTTP with:
- schema validation
- idempotency keys
- retry with exponential backoff
- dead-letter queue persistence on terminal failure
- correlation and run metadata
"""

import json
import logging
import os
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from jsonschema import ValidationError, validate


logger = logging.getLogger(__name__)


@dataclass
class PublisherConfig:
    consumer_url: Optional[str]
    consumer_api_key: Optional[str]
    timeout_seconds: float = 10.0
    max_attempts: int = 3
    backoff_base_seconds: float = 0.5
    dlq_dir: str = "dlq"


class InstructionPublisher:
    """Publishes Prompt Runner instructions to external consumers."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.config = PublisherConfig(
            consumer_url=os.getenv("CONSUMER_URL"),
            consumer_api_key=os.getenv("CONSUMER_API_KEY"),
            timeout_seconds=float(os.getenv("PUBLISH_TIMEOUT_SECONDS", "10")),
            max_attempts=int(os.getenv("PUBLISH_MAX_ATTEMPTS", "3")),
            backoff_base_seconds=float(os.getenv("PUBLISH_BACKOFF_BASE_SECONDS", "0.5")),
            dlq_dir=os.getenv("PUBLISH_DLQ_DIR", "dlq"),
        )

        self._instruction_schema = self._load_instruction_schema()

    def is_configured(self) -> bool:
        return bool(self.config.consumer_url and self.config.consumer_api_key)

    def publish(self, instruction: Dict[str, Any], source: str = "prompt_runner") -> Dict[str, Any]:
        """Publish an instruction with retries and DLQ fallback."""
        run_id = self._new_run_id()
        instruction_id = self._new_instruction_id()
        correlation_id = run_id
        timestamp = self._now_iso()

        schema_ok, schema_error = self._validate_instruction(instruction)
        if not schema_ok:
            return {
                "status": "error",
                "error": "instruction_schema_validation_failed",
                "message": schema_error,
                "run_id": run_id,
                "instruction_id": instruction_id,
                "correlation_id": correlation_id,
            }

        envelope = {
            "run_id": run_id,
            "instruction_id": instruction_id,
            "correlation_id": correlation_id,
            "timestamp": timestamp,
            "source": source,
            "instruction": instruction,
        }

        if not self.is_configured():
            reason = "CONSUMER_URL or CONSUMER_API_KEY is not configured"
            dlq_path = self._write_dlq(envelope, reason)
            return {
                "status": "error",
                "error": "publisher_not_configured",
                "message": reason,
                "run_id": run_id,
                "instruction_id": instruction_id,
                "correlation_id": correlation_id,
                "dlq_path": str(dlq_path.relative_to(self.base_dir)),
            }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.consumer_api_key}",
            "Idempotency-Key": run_id,
            "X-Correlation-ID": correlation_id,
            "X-Instruction-ID": instruction_id,
        }

        last_error = "unknown delivery failure"
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                response = requests.post(
                    self.config.consumer_url,
                    json=envelope,
                    headers=headers,
                    timeout=self.config.timeout_seconds,
                )
                if 200 <= response.status_code < 300:
                    return {
                        "status": "success",
                        "run_id": run_id,
                        "instruction_id": instruction_id,
                        "correlation_id": correlation_id,
                        "http_status": response.status_code,
                        "attempts": attempt,
                        "consumer_url": self.config.consumer_url,
                    }

                last_error = f"HTTP {response.status_code}: {response.text[:300]}"
                logger.warning("Publish attempt %s failed: %s", attempt, last_error)
            except requests.RequestException as exc:
                last_error = str(exc)
                logger.warning("Publish attempt %s raised exception: %s", attempt, last_error)

            if attempt < self.config.max_attempts:
                delay = self.config.backoff_base_seconds * (2 ** (attempt - 1))
                time.sleep(delay)

        dlq_path = self._write_dlq(envelope, last_error)
        return {
            "status": "error",
            "error": "publish_failed",
            "message": last_error,
            "run_id": run_id,
            "instruction_id": instruction_id,
            "correlation_id": correlation_id,
            "attempts": self.config.max_attempts,
            "consumer_url": self.config.consumer_url,
            "dlq_path": str(dlq_path.relative_to(self.base_dir)),
        }

    def _load_instruction_schema(self) -> Dict[str, Any]:
        """Load instruction schema from contract.json or instruction_schema.json."""
        contract_path = self.base_dir / "contract.json"
        if contract_path.exists():
            with open(contract_path, "r", encoding="utf-8") as f:
                contract = json.load(f)
            instruction = contract.get("definitions", {}).get("instruction")
            if instruction:
                return instruction

        schema_path = self.base_dir / "instruction_schema.json"
        if schema_path.exists():
            with open(schema_path, "r", encoding="utf-8") as f:
                return json.load(f)

        raise FileNotFoundError("No instruction schema found (contract.json or instruction_schema.json)")

    def _validate_instruction(self, instruction: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        try:
            validate(instance=instruction, schema=self._instruction_schema)
            return True, None
        except ValidationError as exc:
            return False, exc.message

    def _write_dlq(self, envelope: Dict[str, Any], reason: str) -> Path:
        dlq_dir = self.base_dir / self.config.dlq_dir
        dlq_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{envelope['run_id']}.json"
        file_path = dlq_dir / filename

        payload = {
            "failed_at": self._now_iso(),
            "reason": reason,
            "payload": envelope,
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)

        return file_path

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _new_run_id() -> str:
        return f"RUN-{uuid.uuid4()}"

    @staticmethod
    def _new_instruction_id() -> str:
        return f"INS-{uuid.uuid4()}"
