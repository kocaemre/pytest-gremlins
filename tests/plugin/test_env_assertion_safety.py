"""Keep assertion rewriting from displaying a process or subprocess environment."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest


@pytest.mark.medium
class DescribeEnvironmentAssertionSafety:
    """Assertions should expose only the scalar under test."""

    def it_keeps_environment_mappings_out_of_assertions(self) -> None:
        """A failed assertion must not print a full environment mapping."""
        tests = Path(__file__).resolve().parents[1]
        unsafe: list[str] = []
        for path in tests.rglob('test_*.py'):
            tree = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
            trees = [tree]
            trees.extend(
                ast.parse(node.value)
                for node in ast.walk(tree)
                if isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and 'assert ' in node.value
                and 'os.environ' in node.value
            )
            unsafe.extend(
                f'{path.relative_to(tests)}:{assertion.lineno}'
                for source_tree in trees
                for assertion in ast.walk(source_tree)
                if isinstance(assertion, ast.Assert)
                and any(
                    (isinstance(node, ast.Name) and node.id == 'captured_env')
                    or (
                        isinstance(node, ast.Attribute)
                        and isinstance(node.value, ast.Name)
                        and node.value.id == 'os'
                        and node.attr == 'environ'
                    )
                    or (
                        isinstance(node, ast.Subscript)
                        and isinstance(node.value, ast.Name)
                        and node.value.id == 'kwargs'
                        and isinstance(node.slice, ast.Constant)
                        and node.slice.value == 'env'
                    )
                    for node in ast.walk(assertion.test)
                )
            )
        assert unsafe == []
