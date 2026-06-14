#!/usr/bin/env python3
"""Merge result CSV files and split rows into parameter-range groups."""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Merge CSV files in a folder into merged_data.csv, then group rows "
            "into by_<parameter>/ CSV files according to parameter ranges."
        )
    )

    parser.add_argument(
        "--path",
        type=str,
        default=".",
        help="Path to the directory containing final result CSV files.",
    )
    
    parser.add_argument(
        "--data-folder",
        type=str,
        default="data",
        help="Name of the data folder under --path.",
    )

    parser.add_argument(
        "--parameter",
        required=True,
        help="Column name whose numeric values define the groups.",
    )
    parser.add_argument(
        "--group_range",
        type=float,
        help="Bucket size. For example, 10 creates 0-10, 11-20, 21-30, ...",
    )
    parser.add_argument(
        "--bucket-mode",
        choices=("one-based", "zero-based"),
        default="one-based",
        help=(
            "Range style: one-based creates 0-10, 11-20, ...; "
            "zero-based creates 0-9, 10-19, ..."
        ),
    )
    parser.add_argument(
        "--no-bucket",
        action="store_true",
        help="Create one grouped CSV per unique parameter value instead of bucketing.",
    )
    parser.add_argument(
        "--parameter-source",
        choices=("column", "description"),
        default="column",
        help="Read the grouping parameter from the CSV column or matching description file.",
    )
    parser.add_argument(
        "--description-folder",
        type=str,
        default="descriptions",
        help="Description folder under --path, used with --parameter-source=description.",
    )
    parser.add_argument(
        "--add-sip-columns",
        action="store_true",
        help="Add AVG SIP, MAX SIP and MIN SIP columns from SIP1 and SIP2 before grouping.",
    )
    return parser.parse_args()


def get_parameter_from_description(
    description_path: Path, parameter: str
) -> str:
    description = description_path.read_text()
    match = re.search(rf"\b{re.escape(parameter)}=([0-9]+(?:\.[0-9]+)?)", description)
    if not match:
        raise ValueError(f"Could not find {parameter!r} in {description_path}")
    return match.group(1)


def group_bounds(
    value: float, group_range: float, bucket_mode: str
) -> tuple[int, int]:
    if bucket_mode == "zero-based":
        bucket = math.floor(value / group_range)
        start = int(bucket * group_range)
        end = int((bucket + 1) * group_range - 1)
        return start, end

    if value < 0:
        bucket = math.floor(value / group_range)
        start = int(bucket * group_range)
        end = int((bucket + 1) * group_range)
        return start, end

    bucket = max(0, math.ceil(value / group_range) - 1)
    start = int(bucket * group_range + (1 if bucket else 0))
    end = int((bucket + 1) * group_range)
    return start, end


def read_csv_rows(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open(newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"{csv_path} has no header")
        return reader.fieldnames, list(reader)


def write_csv(csv_path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def add_sip_columns(row: dict[str, str]) -> None:
    sip1 = float(row["SIP1"])
    sip2 = float(row["SIP2"])
    row["AVG SIP"] = str((sip1 + sip2) / 2)
    row["MAX SIP"] = str(max(sip1, sip2))
    row["MIN SIP"] = str(min(sip1, sip2))


def value_sort_key(value: str) -> tuple[int, float | str]:
    try:
        return (0, float(value))
    except ValueError:
        return (1, value)


def value_to_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())


def main() -> None:
    args = parse_args()
    path=Path(args.path)
    data = path / args.data_folder
    descriptions = path / args.description_folder
    parameter = args.parameter
    group_range = args.group_range

    if not args.no_bucket and group_range is None:
        raise ValueError("--group_range is required unless --no-bucket is used")
    if group_range is not None and group_range <= 0:
        raise ValueError("group_range must be positive")

    csv_paths = sorted(
        path
        for path in data.glob("*.csv")
        if path.name != "merged_data.csv"
    )
    if not csv_paths:
        raise ValueError(f"No CSV files found in {data}")

    fieldnames: list[str] = []
    seen_fieldnames: set[str] = set()
    merged_rows: list[dict[str, str]] = []
    for csv_path in csv_paths:
        current_fieldnames, rows = read_csv_rows(csv_path)
        if args.parameter_source == "description":
            description_path = descriptions / f"{csv_path.stem}.txt"
            parameter_value = get_parameter_from_description(description_path, parameter)
            if parameter not in current_fieldnames:
                current_fieldnames.append(parameter)
            for row in rows:
                row[parameter] = parameter_value

        if args.add_sip_columns:
            for required_field in ("SIP1", "SIP2"):
                if required_field not in current_fieldnames:
                    raise ValueError(f"Column {required_field!r} not found in {csv_path}")
            for fieldname in ("AVG SIP", "MAX SIP", "MIN SIP"):
                if fieldname not in current_fieldnames:
                    current_fieldnames.append(fieldname)
            for row in rows:
                add_sip_columns(row)

        if parameter not in current_fieldnames:
            raise ValueError(f"Column {parameter!r} not found in {csv_path}")

        for fieldname in current_fieldnames:
            if fieldname not in seen_fieldnames:
                fieldnames.append(fieldname)
                seen_fieldnames.add(fieldname)

        merged_rows.extend(rows)

    normalized_rows = [
        {fieldname: row.get(fieldname, "") for fieldname in fieldnames}
        for row in merged_rows
    ]
    write_csv(path / "merged_data.csv", fieldnames, normalized_rows)
    if args.no_bucket:
        group_folder = path / f"by_{parameter}"
    else:
        group_folder = path / f"by_{parameter}({int(group_range)})"
    if args.no_bucket:
        grouped_rows_by_value: dict[str, list[dict[str, str]]] = {}
        for row in normalized_rows:
            grouped_rows_by_value.setdefault(row[parameter], []).append(row)

        for value, rows in sorted(grouped_rows_by_value.items(), key=lambda item: value_sort_key(item[0])):
            write_csv(group_folder / f"{value_to_filename(value)}.csv", fieldnames, rows)
        group_count = len(grouped_rows_by_value)
    else:
        grouped_rows_by_bucket: dict[tuple[int, int], list[dict[str, str]]] = {}
        for row in normalized_rows:
            value = float(row[parameter])
            bounds = group_bounds(value, group_range, args.bucket_mode)
            grouped_rows_by_bucket.setdefault(bounds, []).append(row)

        for (start, end), rows in sorted(grouped_rows_by_bucket.items()):
            write_csv(group_folder / f"{start}-{end}.csv", fieldnames, rows)
        group_count = len(grouped_rows_by_bucket)

    print(
        f"Merged {len(csv_paths)} files into merged_data.csv and wrote "
        f"{group_count} grouped files under {group_folder}."
    )


if __name__ == "__main__":
    main()
