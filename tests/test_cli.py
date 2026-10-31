from testlens.cli import create_parser


def test_version_option():
    try:
        create_parser().parse_args(["--version"])
    except SystemExit as exc:
        assert exc.code == 0
    else:
        raise AssertionError("--version should exit")
