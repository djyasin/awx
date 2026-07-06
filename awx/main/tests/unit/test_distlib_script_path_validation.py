"""
Tests for distlib script path validation patch.

Verifies that the patch to pip/_vendor/distlib/scripts.py correctly prevents
script names containing path traversal sequences or absolute paths from
escaping the target directory during wheel installation.
"""

import inspect
import os
import tempfile

import pytest

from pip._vendor.distlib.scripts import ScriptMaker

_patch_applied = 'commonpath' in inspect.getsource(ScriptMaker._write_script)
requires_patch = pytest.mark.skipif(
    not _patch_applied,
    reason='distlib script path validation patch not applied (run: make patch_pip)',
)


class TestDistlibPathTraversalMitigation:
    """Verify that pip's vendored distlib rejects path-traversing script names."""

    @requires_patch
    def test_patch_is_applied(self):
        """Verify the script path validation patch is present in the installed distlib."""
        assert _patch_applied, 'distlib script path validation patch is NOT applied. Run: make patch_pip'

    @requires_patch
    def test_traversal_name_rejected(self):
        """Path-traversing script names like ../../outside must be rejected."""
        with tempfile.TemporaryDirectory() as target_dir:
            maker = ScriptMaker(source_dir=target_dir, target_dir=target_dir)
            maker.variants = {''}
            maker.set_mode = False
            with pytest.raises(ValueError, match='path traversal'):
                maker._write_script(
                    names=['../../outside'],
                    shebang=b'#!/usr/bin/python3\n',
                    script_bytes=b'# test\n',
                    filenames=[],
                    ext='py',
                )

    @requires_patch
    def test_absolute_path_rejected(self):
        """Absolute paths in script names must be rejected."""
        with tempfile.TemporaryDirectory() as target_dir:
            maker = ScriptMaker(source_dir=target_dir, target_dir=target_dir)
            maker.variants = {''}
            maker.set_mode = False
            with pytest.raises(ValueError, match='path traversal'):
                maker._write_script(
                    names=['/tmp/absolute-escape'],
                    shebang=b'#!/usr/bin/python3\n',
                    script_bytes=b'# test\n',
                    filenames=[],
                    ext='py',
                )

    @requires_patch
    def test_normal_script_name_works(self):
        """Normal (non-traversing) script names must still work."""
        with tempfile.TemporaryDirectory() as target_dir:
            maker = ScriptMaker(source_dir=target_dir, target_dir=target_dir)
            maker.variants = {''}
            maker.set_mode = False
            filenames = []
            maker._write_script(
                names=['normal-script'],
                shebang=b'#!/usr/bin/python3\n',
                script_bytes=b'# test\n',
                filenames=filenames,
                ext='py',
            )
            expected_path = os.path.join(target_dir, 'normal-script')
            assert os.path.exists(expected_path), f'Expected script at {expected_path} was not created'
