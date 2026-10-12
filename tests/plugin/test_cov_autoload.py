"""Regression coverage for pytest-cov option forwarding when plugin autoload is disabled."""

from __future__ import annotations

import pytest


@pytest.mark.medium
class DescribeCovAutoload:
    """The gremlin subprocess receives only options registered in the parent session."""

    def it_runs_gremlins_without_loading_pytest_cov(
        self, pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An installed but unloaded pytest-cov cannot register --no-cov."""
        pytester.makepyfile(target='def is_adult(age):\n    return age >= 18\n')
        pytester.makepyfile(test_target='from target import is_adult\n\ndef test_age():\n    assert is_adult(21)\n')
        monkeypatch.setenv('PYTEST_DISABLE_PLUGIN_AUTOLOAD', '1')
        result = pytester.runpytest_subprocess(
            '-p',
            'pytest_gremlins.plugin',
            '-p',
            'xdist.plugin',
            '--gremlins',
            '--gremlin-targets=target.py',
        )
        result.assert_outcomes(passed=1)
        output = result.stdout.str() + result.stderr.str()
        assert 'unrecognized arguments: --no-cov' not in output
        assert 'Zapped:' in output or 'Survived:' in output

    def it_keeps_cov_enabled_for_the_parent_when_loaded_explicitly(
        self, pytester: pytest.Pytester, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """An explicitly registered pytest-cov plugin is still supported."""
        pytester.makepyfile(target='def is_adult(age):\n    return age >= 18\n')
        pytester.makepyfile(test_target='from target import is_adult\n\ndef test_age():\n    assert is_adult(21)\n')
        monkeypatch.setenv('PYTEST_DISABLE_PLUGIN_AUTOLOAD', '1')
        result = pytester.runpytest_subprocess(
            '-p',
            'pytest_gremlins.plugin',
            '-p',
            'xdist.plugin',
            '-p',
            'pytest_cov',
            '--gremlins',
            '--gremlin-targets=target.py',
        )
        result.assert_outcomes(passed=1)
        output = result.stdout.str() + result.stderr.str()
        assert 'unrecognized arguments: --no-cov' not in output
