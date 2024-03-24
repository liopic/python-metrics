import argparse
import ast
import os
from dataclasses import dataclass
from glob import glob

import pandas as pd


@dataclass
class FunctionMetrics:
    class_name: str
    function_name: str
    statement_count: int


class MetricsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.current_class = None
        self.current_function = None
        self.functions: list[FunctionMetrics] = []
        self.statement_count:int = 0

    def visit_ClassDef(self, node: ast.ClassDef):
        self.current_class = node.name
        self.statement_count = 0
        self.generic_visit(node)
        self.current_class = None

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.current_function = node.name
        self.statement_count = 0
        self.generic_visit(node)
        self.functions.append(
            FunctionMetrics(
                self.current_class, self.current_function, self.statement_count
            )
        )
        self.current_function = None

    def generic_visit(self, node: ast.AST):
        if isinstance(node, ast.stmt) and not isinstance(node, ast.FunctionDef):
            self.statement_count += 1
        super().generic_visit(node)

    def get_function_metrics(self) -> list[FunctionMetrics]:
        return self.functions


def extract_functions(filename):
    with open(filename, "r") as file:
        source_code = file.read()
        visitor = MetricsVisitor()
        visitor.visit(ast.parse(source_code))
        functions = visitor.get_function_metrics()
        return functions


def get_all_python_files(path: str) -> list[str]:
    if os.path.isdir(path):
        return [file for file in glob(f"{path}/**/*.py", recursive=True)]
    if path.endswith(".py"):
        return [path]
    raise ValueError("Path must be a python file or a directory")


def analyse_path(path) -> pd.DataFrame:
    file_metrics = []
    for filename in get_all_python_files(path):
        functions = extract_functions(filename)
        if functions:
            df = pd.DataFrame(functions)
            df.insert(0, "file", filename)
            df["statement_count"] = df["statement_count"].astype(int)
            file_metrics.append(df)
    return pd.concat(file_metrics)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("path", help="The path to analyse")
    args = arg_parser.parse_args()
    if args.path:
        path = args.path
    else:
        path = "example.py"

    df = analyse_path(path)
    df.to_csv("metrics.csv", index=False)

    average_statement_count = df["statement_count"].mean()
    print(f"Average statement count: {average_statement_count:.2f}")
