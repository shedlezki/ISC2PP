#!/usr/bin/env python3
"""Generate TEMP-style normalized magnitude results and their summary."""

from __future__ import annotations

import ast
import csv
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "final"
DESCRIPTION_DIR = ROOT / "descriptions"
NORMALIZED_DIR = ROOT / "normalized"
SUMMARY_PATH = ROOT / "summary.csv"
VARIANCE_PATH = ROOT / "variance.csv"
STANDARD_DEVIATION_PATH = ROOT / "standard_deviation.csv"

NORMALIZED_COLUMNS = [
    "eid",
    "SIP",
    "SCP",
    "Individual Time In Optimal Social Welfare",
    "Individual Time In Min-Max",
    "Individual Time In Min-Sum",
    "Individual Time In Max-Min-Surplus",
    "Individual Time In Nash",
    "Individual Time In Kalai_Smorodinsky",
    "Individual Time In Egalitarian",
    "Individual Time In Utilitarian",
    "Optimal Social Welfare",
    "Min-Max",
    "Min-Sum",
    "Max-Min Improvement",
    "Nash",
    "Kalai_Smorodinsky",
    "Egalitarian",
    "Utilitarian",
    "SIP|SIP",
    "PoA",
    "PoS",
]

SUMMARY_COLUMNS = [
    column for column in NORMALIZED_COLUMNS if column not in {"eid"}
]
MULTI_PAIR_POTENTIAL_COLUMN = "Elements With Multiple Potential Pairs"
AVG_POTENTIAL_PAIRS_COLUMN = "Average Potential PNEs"


def label_suffix(label: str) -> str:
    return f"_{label}" if label else ""


def ratio(numerator: str | float, denominator: float) -> str | float:
    return "" if denominator == 0 else float(numerator) / denominator


def normalize(row: dict[str, str]) -> dict[str, str | float]:
    individual_baseline = float(row["SIP1"])
    social_welfare_baseline = float(row["Optimal Social Welfare"])

    return {
        "eid": row["eid"],
        "SIP": ratio(row["SIP1"], individual_baseline),
        "SCP": ratio(row["SCP1"], individual_baseline),
        "Individual Time In Optimal Social Welfare": ratio(
            row["Individual Time In Optimal Social Welfare"], individual_baseline
        ),
        "Individual Time In Min-Max": ratio(
            row["Individual Time In Min-Max"], individual_baseline
        ),
        "Individual Time In Min-Sum": ratio(
            row["Individual Time In Min-Sum"], individual_baseline
        ),
        "Individual Time In Max-Min-Surplus": ratio(
            row["Individual Time In Max-Min-Surplus"], individual_baseline
        ),
        "Individual Time In Nash": ratio(
            row["Individual Time In Nash"], individual_baseline
        ),
        "Individual Time In Kalai_Smorodinsky": ratio(
            row["Individual Time In Kalai_Smorodinsky"], individual_baseline,
        ),
        "Individual Time In Egalitarian": ratio(
            row["Individual Time In Egalitarian"], individual_baseline
        ),
        "Individual Time In Utilitarian": ratio(
            row["Individual Time In Utilitarian"], individual_baseline
        ),
        "Optimal Social Welfare": 1.0,
        "Min-Max": ratio(row["Min-Max"], social_welfare_baseline),
        "Min-Sum": ratio(row["Min-Sum"], social_welfare_baseline),
        "Max-Min Improvement": ratio(
            row["Max-Min-Surplus"], social_welfare_baseline
        ),
        "Nash": ratio(row["Nash"], social_welfare_baseline),
        "Kalai_Smorodinsky": ratio(
            row["Kalai_Smorodinsky"], social_welfare_baseline
        ),
        "Egalitarian": ratio(row["Egalitarian"], social_welfare_baseline),
        "Utilitarian": ratio(row["Utilitarian"], social_welfare_baseline),
        "SIP|SIP": ratio(
            float(row["SIP1"]) + float(row["SIP2"]), social_welfare_baseline
        ),
        "PoA": float(row["PoA"]),
        "PoS": float(row["PoS"]),
    }


def get_parameter(experiment_name: str, parameter:str) -> float:
    description_path = DESCRIPTION_DIR / f"{experiment_name}.txt"
    description = description_path.read_text()
    match = re.search(rf"\b{parameter}=([0-9]+(?:\.[0-9]+)?)", description)
    if not match:
        raise ValueError(f"Could not find {parameter} in {experiment_name}.txt")
    return float(match.group(1))


def experiment_number(path: Path) -> int:
    match = re.fullmatch(r"exp(\d+)\.csv", path.name)
    if not match:
        raise ValueError(f"Unexpected final result filename: {path.name}")
    return int(match.group(1))


def result_sort_key(path: Path) -> tuple[int, float, float, str]:
    experiment_match = re.fullmatch(r"exp(\d+)\.csv", path.name)
    if experiment_match:
        experiment_number_value = float(experiment_match.group(1))
        return (0, experiment_number_value, experiment_number_value, path.name)

    interval_match = re.fullmatch(
        r"(-?\d+(?:\.\d+)?)-(-?\d+(?:\.\d+)?)", path.stem
    )
    if interval_match:
        return (
            1,
            float(interval_match.group(1)),
            float(interval_match.group(2)),
            path.name,
        )

    return (2, 0, 0, path.name)


def experiment_name(path: Path) -> str:
    return path.stem


def average_rows(rows: list[dict[str, str | float]]) -> dict[str, float]:
    result = {}
    for column in SUMMARY_COLUMNS:
        values = [float(row[column]) for row in rows if row[column] != ""]
        result[column] = sum(values) / len(values) if values else "NA"
    return result


def variance_rows(rows: list[dict[str, str | float]]) -> dict[str, float]:
    result = {}
    for column in SUMMARY_COLUMNS:
        values = [float(row[column]) for row in rows if row[column] != ""]
        if not values:
            result[column] = "NA"
            continue

        average = sum(values) / len(values)
        result[column] = sum((value - average) ** 2 for value in values) / len(values)
    return result


def standard_deviation_from_variance(
    variance_row: dict[str, str | float]
) -> dict[str, str | float]:
    return {
        column: value if value == "NA" else math.sqrt(float(value))
        for column, value in variance_row.items()
    }


def count_elements_with_multiple_potential_pairs(rows: list[dict[str, str]]) -> int:
    matching_eids = set()
    for row in rows:
        if number_of_potential_pairs(row)>1:
            matching_eids.add(row["eid"])
    return 2*len(matching_eids)

def avg_potential_pairs(rows: list[dict[str, str]]) -> int:
    if not rows:
        return "NA"
    sum = 0
    for row in rows:
        sum += number_of_potential_pairs(row)  
    return sum / len(rows)


def variance_potential_pairs(rows: list[dict[str, str]]) -> str | float:
    if not rows:
        return "NA"
    values = [number_of_potential_pairs(row) for row in rows]
    average = sum(values) / len(values)
    return sum((value - average) ** 2 for value in values) / len(values)


def number_of_potential_pairs(row: dict[str, str]) -> bool:
    return len(ast.literal_eval(row["Potential"]))


def parseArguments():
    import argparse

    parser = argparse.ArgumentParser(
        description="Normalize final results and generate summary."
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
        type=str,
        default="magnitude",
        help="Parameter to extract from description files for summary.",
    )
    parser.add_argument(
        "--comparison-source",
        choices=("description", "filename"),
        default="description",
        help="Read the comparison parameter from description files or use CSV file names.",
    )
    parser.add_argument(
        "--filter-multiple-pne",
        action="store_true",
        help="Normalize and summarize only rows with multiple potential PNEs.",
    )
    parser.add_argument(
        "--label",
        type=str,
        default="",
        help="Suffix label for the normalized folder, summary CSV, and variance CSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parseArguments()
    global DATA_DIR, DESCRIPTION_DIR, NORMALIZED_DIR
    global SUMMARY_PATH, VARIANCE_PATH, STANDARD_DEVIATION_PATH
    DATA_DIR = Path(args.path) / args.data_folder
    DESCRIPTION_DIR = Path(args.path) / "descriptions"
    suffix = label_suffix(args.label)
    SUB_FOLDER = Path(args.path) / args.label
    NORMALIZED_DIR = SUB_FOLDER / f"normalized{suffix}"
    SUMMARY_PATH = SUB_FOLDER / f"summary{suffix}.csv"
    VARIANCE_PATH = SUB_FOLDER / f"variance{suffix}.csv"
    STANDARD_DEVIATION_PATH = SUB_FOLDER / f"standard_deviation{suffix}.csv"

    SUB_FOLDER.mkdir(exist_ok=True)
    NORMALIZED_DIR.mkdir(exist_ok=True)
    summary_rows: list[dict[str, str | float]] = []
    variance_rows_output: list[dict[str, str | float]] = []
    standard_deviation_rows_output: list[dict[str, str | float]] = []

    source_paths = (
        DATA_DIR.glob("*.csv")
        if args.comparison_source == "filename"
        else DATA_DIR.glob("exp*.csv")
    )
    sort_key = (
        result_sort_key
        if args.comparison_source == "filename"
        else experiment_number
    )
    for source_path in sorted(source_paths, key=sort_key):
        current_experiment_name = experiment_name(source_path)
        #todo: i want the columns in the normalized files to be stored in a consistent order:
        # SIP,SCP,Individual Time In Optimal Social Welfare,Individual Time In Min-Max,Individual Time In Min-Sum,Individual Time In Max-Min-Surplus,Individual Time In Nash,Individual Time In Kalai_Smorodinsky,Individual Time In Egalitarian,Individual Time In Utilitarian,Min-Max,Min-Sum,Max-Min Improvement,Nash,Kalai_Smorodinsky,Egalitarian,Utilitarian,SIP|SIP,PoA,PoS
        with source_path.open(newline="") as source_file:
            source_rows = list(csv.DictReader(source_file))
            if args.filter_multiple_pne:
                source_rows = [
                    row for row in source_rows if number_of_potential_pairs(row)>1
                ]
            normalized_rows = [normalize(row) for row in source_rows]

        output_path = NORMALIZED_DIR / f"{current_experiment_name}_normalized.csv"
        with output_path.open("w", newline="") as output_file:
            writer = csv.DictWriter(output_file, fieldnames=NORMALIZED_COLUMNS)
            writer.writeheader()
            writer.writerows(normalized_rows)

        parameter_value = (
            current_experiment_name
            if args.comparison_source == "filename"
            else get_parameter(current_experiment_name, args.parameter)
        )
        summary_rows.append(
            {
                args.parameter: parameter_value,
                MULTI_PAIR_POTENTIAL_COLUMN: count_elements_with_multiple_potential_pairs(
                    source_rows
                ),
                AVG_POTENTIAL_PAIRS_COLUMN: avg_potential_pairs(source_rows),
                **average_rows(normalized_rows),
            }
        )
        current_variance_row = variance_rows(normalized_rows)
        current_potential_pairs_variance = variance_potential_pairs(source_rows)
        variance_rows_output.append(
            {
                args.parameter: parameter_value,
                AVG_POTENTIAL_PAIRS_COLUMN: current_potential_pairs_variance,
                **current_variance_row,
            }
        )
        standard_deviation_rows_output.append(
            {
                args.parameter: parameter_value,
                AVG_POTENTIAL_PAIRS_COLUMN: (
                    "NA"
                    if current_potential_pairs_variance == "NA"
                    else math.sqrt(float(current_potential_pairs_variance))
                ),
                **standard_deviation_from_variance(current_variance_row),
            }
        )

    with SUMMARY_PATH.open("w", newline="") as summary_file:
        summary_columns = [
            args.parameter,
            MULTI_PAIR_POTENTIAL_COLUMN,
            AVG_POTENTIAL_PAIRS_COLUMN,
            *SUMMARY_COLUMNS,
        ]
        writer = csv.DictWriter(summary_file, fieldnames=summary_columns)
        writer.writeheader()
        writer.writerows(summary_rows)

    with VARIANCE_PATH.open("w", newline="") as variance_file:
        variance_columns = [args.parameter, AVG_POTENTIAL_PAIRS_COLUMN, *SUMMARY_COLUMNS]
        writer = csv.DictWriter(variance_file, fieldnames=variance_columns)
        writer.writeheader()
        writer.writerows(variance_rows_output)

    with STANDARD_DEVIATION_PATH.open("w", newline="") as standard_deviation_file:
        standard_deviation_columns = [
            args.parameter,
            AVG_POTENTIAL_PAIRS_COLUMN,
            *SUMMARY_COLUMNS,
        ]
        writer = csv.DictWriter(
            standard_deviation_file, fieldnames=standard_deviation_columns
        )
        writer.writeheader()
        writer.writerows(standard_deviation_rows_output)


if __name__ == "__main__":
    main()
