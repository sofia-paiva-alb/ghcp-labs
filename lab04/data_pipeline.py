"""
Lab 4 — Knowledge Bases & Indexed Repos
=========================================
A data pipeline project with intentionally inconsistent coding style.
Participants use custom instructions and knowledge bases to make
Copilot follow project conventions.
"""

import csv
import json
import os
from dataclasses import dataclass
from typing import Any
from pathlib import Path


@dataclass
class PipelineConfig:
    source_dir: str
    output_dir: str
    file_format: str = "csv"  # csv or json
    batch_size: int = 100
    skip_header: bool = True
    delimiter: str = ","


class DataPipeline:
    """Reads, transforms, and outputs data files."""

    def __init__(self, config: PipelineConfig):
        self.config = config
        self._records_processed = 0
        self._errors: list[str] = []

    def run(self) -> dict:
        """Execute the full pipeline. Returns summary dict."""
        records = self._read_source()
        transformed = self._transform(records)
        written = self._write_output(transformed)
        return {
            "records_read": len(records),
            "records_transformed": len(transformed),
            "records_written": written,
            "errors": self._errors,
        }

    def _read_source(self) -> list[dict[str, Any]]:
        """Read all files from source directory."""
        records = []
        source = Path(self.config.source_dir)
        if not source.exists():
            self._errors.append(f"Source directory {source} does not exist")
            return records

        for filepath in source.glob(f"*.{self.config.file_format}"):
            try:
                if self.config.file_format == "csv":
                    records.extend(self._read_csv(filepath))
                elif self.config.file_format == "json":
                    records.extend(self._read_json(filepath))
            except Exception as e:
                self._errors.append(f"Error reading {filepath}: {e}")
        return records

    def _read_csv(self, filepath: Path) -> list[dict[str, Any]]:
        records = []
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=self.config.delimiter)
            for row in reader:
                records.append(dict(row))
        return records

    def _read_json(self, filepath: Path) -> list[dict[str, Any]]:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        return [data]

    def _transform(self, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Apply transformations: strip whitespace, normalize keys, filter empty."""
        transformed = []
        for record in records:
            cleaned = {}
            for key, value in record.items():
                clean_key = key.strip().lower().replace(" ", "_")
                clean_value = value.strip() if isinstance(value, str) else value
                if clean_value:  # skip empty values
                    cleaned[clean_key] = clean_value
            if cleaned:
                transformed.append(cleaned)
                self._records_processed += 1
        return transformed

    def _write_output(self, records: list[dict[str, Any]]) -> int:
        """Write records to output directory in batches."""
        output = Path(self.config.output_dir)
        output.mkdir(parents=True, exist_ok=True)
        written = 0

        for i in range(0, len(records), self.config.batch_size):
            batch = records[i:i + self.config.batch_size]
            batch_num = i // self.config.batch_size + 1
            outfile = output / f"batch_{batch_num:04d}.json"
            with open(outfile, "w", encoding="utf-8") as f:
                json.dump(batch, f, indent=2)
            written += len(batch)

        return written


# ── Validators ───────────────────────────────────────────────────────

def validate_record(record: dict[str, Any], required_fields: list[str]) -> list[str]:
    """Validate a single record. Returns list of error messages."""
    errors = []
    for field in required_fields:
        if field not in record or not record[field]:
            errors.append(f"Missing required field: {field}")
    return errors


def validate_batch(records: list[dict[str, Any]], required_fields: list[str]) -> dict:
    """Validate a batch of records. Returns summary with valid/invalid counts."""
    valid = []
    invalid = []
    for i, record in enumerate(records):
        errors = validate_record(record, required_fields)
        if errors:
            invalid.append({"index": i, "record": record, "errors": errors})
        else:
            valid.append(record)
    return {"valid": valid, "invalid": invalid, "total": len(records)}
