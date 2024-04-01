import argparse
import ast
import os
import queue
from dataclasses import dataclass

import pandas as pd


@dataclass
class FunctionMetrics:
    class_name: str
    function_name: str
    statement_count: int
    statement_lines: list[int]


class MetricsVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.classes = queue.LifoQueue()
        self.classes.put("")
        self.current_class = ""
        self.functions = queue.LifoQueue()
        self.functions.put("")
        self.current_function = ""
        self.visited_functions = []
        self.statement_count: int = 0
        self.statement_lines: list[int] = []

    def _reset_statements(self):
        self.statement_count = 0
        self.statement_lines = []

    def visit_ClassDef(self, node: ast.ClassDef):
        self.classes.put(node.name)
        self.current_class = node.name
        super().generic_visit(node)
        self.classes.get()
        #assign current_class to top of queue
        self.current_class = self.classes.queue[-1]

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.functions.put(node.name)
        self.function_name = node.name
        self._reset_statements()
        super().generic_visit(node)
        self.function_name = self.functions.get()
        self.visited_functions.append(
            FunctionMetrics(
                self.current_class,
                self.function_name,
                self.statement_count,
                self.statement_lines,
            )
        )
        self._reset_statements()

    def generic_visit(self, node: ast.AST):
        if isinstance(node, ast.stmt):
            self.statement_count += 1
            self.statement_lines.append(node.lineno)
        super().generic_visit(node)

    def get_function_metrics(self) -> list[FunctionMetrics]:
        return self.visited_functions


def extract_functions(filename):
    with open(filename, "r") as file:
        source_code = file.read()
        visitor = MetricsVisitor()
        visitor.visit(ast.parse(source_code))
        functions = visitor.get_function_metrics()
        return functions


def get_all_python_files(path: str, exclude: str) -> list[str]:
    python_files = []
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if exclude not in root and file.endswith(".py"):
                    python_files.append(os.path.join(root, file))
        return python_files
    if path.endswith(".py"):
        return [path]
    raise ValueError("Path must be a python file or a directory")


def analyse_path(path: str, exclude: str) -> pd.DataFrame:
    file_metrics = []
    python_files = get_all_python_files(path, exclude)
    for filename in python_files:
        functions = extract_functions(filename)
        if functions:
            df = pd.DataFrame(functions)
            df.insert(0, "file", filename)
            df["statement_count"] = df["statement_count"].astype(int)
            file_metrics.append(df)
    return pd.concat(file_metrics)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("path", help="The path to analyse", type=str)
    arg_parser.add_argument(
        "--exclude", help="The path to exclude", type=str, default=""
    )
    args = arg_parser.parse_args()
    df = analyse_path(args.path, args.exclude)
    df.to_csv("metrics.csv", index=False)

    average_statement_count = df["statement_count"].mean()
    print(f"Average statement count: {average_statement_count:.2f}")
    quantiles = df["statement_count"].quantile([0.25, 0.5, 0.75])
    print(f"Quantiles:\n{quantiles}")
