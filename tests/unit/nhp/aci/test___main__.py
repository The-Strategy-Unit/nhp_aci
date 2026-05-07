from unittest.mock import Mock, mock_open, patch

import pytest

from nhp.aci.__main__ import _arg_parser, _run, _status, main


class TestArgParser:
    class TestRun:
        def test_defaults(self):
            parser = _arg_parser()
            args = parser.parse_args(
                [
                    "run",
                    "id",
                ]
            )

            assert args.command == "run"
            assert args.params == "id"
            assert args.app_version is None
            assert args.dataset is None
            assert not args.save_full_model_results
            assert args.timeout == "60m"

        def test_app_version(self):
            parser = _arg_parser()
            args = parser.parse_args(["run", "id", "--app-version", "dev"])

            assert args.command == "run"
            assert args.params == "id"
            assert args.app_version == "dev"
            assert args.dataset is None
            assert not args.save_full_model_results
            assert args.timeout == "60m"

        def test_dataset(self):
            parser = _arg_parser()
            args = parser.parse_args(["run", "id", "--dataset", "dataset"])

            assert args.command == "run"
            assert args.params == "id"
            assert args.app_version is None
            assert args.dataset == "dataset"
            assert not args.save_full_model_results
            assert args.timeout == "60m"

        def test_save_full_model_results(self):
            parser = _arg_parser()
            args = parser.parse_args(["run", "id", "--save-full-model-results"])

            assert args.command == "run"
            assert args.params == "id"
            assert args.app_version is None
            assert args.dataset is None
            assert args.save_full_model_results
            assert args.timeout == "60m"

        def test_timeout(self):
            parser = _arg_parser()
            args = parser.parse_args(["run", "id", "--timeout", "30m"])

            assert args.command == "run"
            assert args.params == "id"
            assert args.app_version is None
            assert args.dataset is None
            assert not args.save_full_model_results
            assert args.timeout == "30m"

    class TestStatus:
        def test_with_model_id(self):
            parser = _arg_parser()
            args = parser.parse_args(
                [
                    "status",
                    "id",
                ]
            )

            assert args.command == "status"
            assert args.model_id == "id"

        def test_without_model_id(self):
            parser = _arg_parser()
            args = parser.parse_args(
                [
                    "status",
                ]
            )

            assert args.command == "status"
            assert args.model_id is None

    class TestClean:
        def test_with_model_id(self):
            parser = _arg_parser()
            args = parser.parse_args(
                [
                    "clean",
                    "id",
                ]
            )

            assert args.command == "clean"
            assert args.model_id == "id"


class TestRun:
    def test_just_params_file_with_app_version_in_params(self, mocker):
        # arrange
        args = Mock()
        args.params = "file.json"
        args.save_full_model_results = False
        args.results_viewable = False
        args.timeout = "60m"
        args.app_version = None
        args.dataset = None

        m_open = mock_open(read_data='{"app_version": "v1"}')

        m_create = mocker.patch("nhp.aci.__main__.create_model_run", return_value={"id": "id"})

        m_print = mocker.patch("builtins.print")

        # act
        with patch("builtins.open", m_open):
            _run(args)

        # assert
        m_open.assert_called_once_with("file.json", "r", encoding="UTF-8")
        m_create.assert_called_once_with(
            params={"app_version": "v1"},
            app_version="v1",
            save_full_model_results=False,
            results_viewable=False,
            timeout="60m",
        )
        m_print.assert_called_once_with("Model run started: id")

    def test_just_params_file_without_app_version_in_params(self, mocker):
        # arrange
        args = Mock()
        args.params = "file.json"
        args.save_full_model_results = False
        args.results_viewable = False
        args.timeout = "60m"
        args.app_version = None
        args.dataset = None

        m_open = mock_open(read_data="{}")

        m_create = mocker.patch("nhp.aci.__main__.create_model_run", return_value={"id": "id"})

        m_print = mocker.patch("builtins.print")

        # act
        with patch("builtins.open", m_open):
            _run(args)

        # assert
        m_open.assert_called_once_with("file.json", "r", encoding="UTF-8")
        m_create.assert_called_once_with(
            params={"app_version": "dev"},
            app_version="dev",
            save_full_model_results=False,
            results_viewable=False,
            timeout="60m",
        )
        m_print.assert_called_once_with("Model run started: id")

    def test_setting_app_version(self, mocker):
        # arrange
        args = Mock()
        args.params = "file.json"
        args.save_full_model_results = False
        args.results_viewable = False
        args.timeout = "60m"
        args.app_version = "v2"
        args.dataset = None

        m_open = mock_open(read_data="{}")

        m_create = mocker.patch("nhp.aci.__main__.create_model_run", return_value={"id": "id"})

        m_print = mocker.patch("builtins.print")

        # act
        with patch("builtins.open", m_open):
            _run(args)

        # assert
        m_open.assert_called_once_with("file.json", "r", encoding="UTF-8")
        m_create.assert_called_once_with(
            params={"app_version": "v2"},
            app_version="v2",
            save_full_model_results=False,
            results_viewable=False,
            timeout="60m",
        )
        m_print.assert_called_once_with("Model run started: id")

    def test_setting_dataset(self, mocker):
        # arrange
        args = Mock()
        args.params = "file.json"
        args.save_full_model_results = False
        args.results_viewable = False
        args.timeout = "60m"
        args.app_version = None
        args.dataset = "dataset"

        m_open = mock_open(read_data="{}")

        m_create = mocker.patch("nhp.aci.__main__.create_model_run", return_value={"id": "id"})

        m_print = mocker.patch("builtins.print")

        # act
        with patch("builtins.open", m_open):
            _run(args)

        # assert
        m_open.assert_called_once_with("file.json", "r", encoding="UTF-8")
        m_create.assert_called_once_with(
            params={"app_version": "dev", "dataset": "dataset"},
            app_version="dev",
            save_full_model_results=False,
            results_viewable=False,
            timeout="60m",
        )
        m_print.assert_called_once_with("Model run started: id")


class TestStatus:
    @pytest.mark.parametrize(
        "complete, expected",
        [
            (
                {"aae": 1, "outpatients": 100, "inpatients": 100},
                "aae: 1",
            ),
            (
                {"aae": 0, "outpatients": 2, "inpatients": 100},
                "op: 2",
            ),
            (
                {"aae": 0, "outpatients": 0, "inpatients": 3},
                "ip: 3",
            ),
        ],
    )
    def test_single_model_run_exists(self, mocker, complete, expected):
        # arrange
        status = {"state": "running", "complete": complete, "model_runs": 100}
        m_status = mocker.patch("nhp.aci.__main__.get_model_run_status", return_value=status)
        args = Mock()
        args.model_id = "id"
        m_print = mocker.patch("builtins.print")

        # act
        _status(args)

        # assert
        m_status.assert_called_once_with("id")
        m_print.assert_called_once_with(f"id: running [{expected}/100]")

    def test_single_model_run_not_exists(self, mocker):
        # arrange
        m_status = mocker.patch("nhp.aci.__main__.get_model_run_status", return_value=None)
        args = Mock()
        args.model_id = "id"
        m_print = mocker.patch("builtins.print")

        # act
        _status(args)

        # assert
        m_status.assert_called_once_with("id")
        m_print.assert_called_once_with("Unknown model id: id")

    def test_all_model_runs_no_runs(self, mocker):
        # arrange
        m_cmr = mocker.patch("nhp.aci.__main__.get_current_model_runs", return_value={})
        args = Mock()
        args.model_id = None
        m_print = mocker.patch("builtins.print")

        # act
        _status(args)

        # assert
        m_cmr.assert_called_once()
        m_print.assert_called_once_with("There are currently no model runs")

    def test_all_model_runs_with_runs(self, mocker):
        # arrange
        m_cmr = mocker.patch(
            "nhp.aci.__main__.get_current_model_runs",
            return_value={"a": {"state": "running"}, "b": {"state": "terminated"}, "c": {}},
        )
        args = Mock()
        args.model_id = None

        print_output = []
        m_print = mocker.patch("builtins.print", side_effect=print_output.append)

        # act
        _status(args)

        # assert
        m_cmr.assert_called_once()
        assert m_print.call_count == 4
        assert print_output == ["Current Model Runs:", "a: running", "b: terminated", "c: unknown"]


class TestMain:
    def test_run(self, mocker):
        # arrange
        m = mocker.patch("nhp.aci.__main__._arg_parser")
        m().parse_args().command = "run"
        m.reset_mock()

        m_run = mocker.patch("nhp.aci.__main__._run")
        m_status = mocker.patch("nhp.aci.__main__._status")
        m_clean = mocker.patch("nhp.aci.__main__.clean_up_model_run")

        # act
        main()

        # assert
        m.assert_called_once()
        m_run.assert_called_once_with(m().parse_args())
        m_status.assert_not_called()
        m_clean.assert_not_called()
        m().print_help.assert_not_called()

    def test_status(self, mocker):
        # arrange
        m = mocker.patch("nhp.aci.__main__._arg_parser")
        m().parse_args().command = "status"
        m.reset_mock()

        m_run = mocker.patch("nhp.aci.__main__._run")
        m_status = mocker.patch("nhp.aci.__main__._status")
        m_clean = mocker.patch("nhp.aci.__main__.clean_up_model_run")

        # act
        main()

        # assert
        m.assert_called_once()
        m_run.assert_not_called()
        m_status.assert_called_once_with(m().parse_args())
        m_clean.assert_not_called()
        m().print_help.assert_not_called()

    def test_clean(self, mocker):
        # arrange
        m = mocker.patch("nhp.aci.__main__._arg_parser")
        m().parse_args().command = "clean"
        m().parse_args().model_id = "id"
        m.reset_mock()

        m_run = mocker.patch("nhp.aci.__main__._run")
        m_status = mocker.patch("nhp.aci.__main__._status")
        m_clean = mocker.patch("nhp.aci.__main__.clean_up_model_run")

        # act
        main()

        # assert
        m.assert_called_once()
        m_run.assert_not_called()
        m_status.assert_not_called()
        m_clean.assert_called_once_with("id")
        m().print_help.assert_not_called()

    def test_help(self, mocker):
        # arrange
        m = mocker.patch("nhp.aci.__main__._arg_parser")
        m().parse_args().command = "UNKNOWN COMMAND"
        m.reset_mock()

        m_run = mocker.patch("nhp.aci.__main__._run")
        m_status = mocker.patch("nhp.aci.__main__._status")
        m_clean = mocker.patch("nhp.aci.__main__.clean_up_model_run")

        # act
        main()

        # assert
        m.assert_called_once()
        m_run.assert_not_called()
        m_status.assert_not_called()
        m_clean.assert_not_called()
        m().print_help.assert_called_once()


def test_init(mocker):
    main_mock = mocker.patch("nhp.aci.__main__.main")

    import nhp.aci.__main__ as m

    m.init()
    main_mock.assert_not_called()

    with patch.object(m, "__name__", "__main__"):
        m.init()
        main_mock.assert_called_once()
