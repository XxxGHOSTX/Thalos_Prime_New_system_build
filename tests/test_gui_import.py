"""
Test for GUI import functionality
"""


def test_gui_import():
    """Test that GUI system can be imported"""
    try:
        from thalos.gui import GUISystem
        assert GUISystem is not None
    except ImportError as e:
        # GUI imports might fail if src/thalos not in path
        import sys
        from pathlib import Path
        # Add src to path
        src_path = Path(__file__).parent.parent / "src"
        if src_path.exists():
            sys.path.insert(0, str(src_path))
            from thalos.gui import GUISystem
            assert GUISystem is not None
        else:
            raise e
