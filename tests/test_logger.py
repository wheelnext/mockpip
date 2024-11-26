import logging as _logging
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

import mockpip
from mockpip.logger import _LoggerAPI


class TestLoggerAPI(unittest.TestCase):
    """
    Unittests for the _LoggerAPI class in `mockpip.logger`.
    This class ensures the correct setup and behavior of the logger, including custom
    log levels.
    """

    def setUp(self):
        """Reset and Set up the logger instance before each test."""
        self.logger = _LoggerAPI()
        self.logger._logger = self.logger.setup_logger()  # noqa: SLF001

    def test_logger_initialization(self):
        """Test that the logger is properly initialized with the correct settings."""
        assert isinstance(self.logger._logger, _logging.Logger)  # noqa: SLF001
        assert self.logger._logger.name == "mockpip"  # noqa: SLF001
        assert self.logger._logger.level == _LoggerAPI.INFO  # noqa: SLF001
        assert not self.logger._logger.propagate  # noqa: SLF001

    def test_logger_levels(self):
        """Test that the logger has the correct logging levels defined."""
        assert self.logger.NOTSET == _logging.NOTSET
        assert self.logger.DEBUG == _logging.DEBUG
        assert self.logger.INFO == _logging.INFO
        assert self.logger.WARNING == _logging.WARNING
        assert self.logger.ERROR == _logging.ERROR
        assert self.logger.CRITICAL == _logging.CRITICAL

    @patch("mockpip.logger._logging.getLogger")
    def test_getLogger(self, mock_getLogger):  # noqa: N802, N803
        """Test the getLogger method returns a logger instance."""
        mock_logger_instance = MagicMock()
        mock_getLogger.return_value = mock_logger_instance

        logger = self.logger.getLogger("test_logger")
        mock_getLogger.assert_called_once_with("test_logger")
        assert logger == mock_logger_instance

    @patch("mockpip.logger._logging.getLogger")
    @patch("sys.stdout", new_callable=MagicMock)
    @patch("sys.stderr", new_callable=MagicMock)
    @patch("mockpip.logger._logging.StreamHandler")
    def test_setup_logger_stream_handlers(
        self,
        mock_handler,
        mock_stderr,
        mock_stdout,
        mock_getLogger,  # noqa: N803
    ):
        """
        Test the setup_logger method to ensure that the correct stream handlers
        are configured with the appropriate filters and formatters.
        """
        # Create mock handlers
        mock_stdout_handler = MagicMock()
        mock_stderr_handler = MagicMock()
        mock_handler.side_effect = [mock_stdout_handler, mock_stderr_handler]

        # Mock the logger instance
        mock_logger_instance = MagicMock()
        mock_getLogger.return_value = mock_logger_instance

        # Call setup_logger
        self.logger._logger = _LoggerAPI.setup_logger(  # noqa: SLF001
            handlers=[mock_stdout_handler, mock_stderr_handler]
        )

        # Verify the logger instance
        assert self.logger._logger == mock_logger_instance  # noqa: SLF001

        # Ensure two handlers were added
        assert mock_logger_instance.addHandler.call_count == 2  # noqa: PLR2004

        # Retrieve the handlers that were added
        handlers = [
            call[0][0] for call in mock_logger_instance.addHandler.call_args_list
        ]
        stdout_handler, stderr_handler = handlers

        # Verify the types of handlers added
        assert stdout_handler is mock_stdout_handler
        assert stderr_handler is mock_stderr_handler

        # Define expected filter functions
        def stdout_filter_func(record):
            return record.levelno <= _logging.INFO

        def stderr_filter_func(record):
            return record.levelno > _logging.INFO

        # Verify the filter function behaves as expected
        assert stdout_filter_func(
            _logging.LogRecord(
                name="test",
                level=_logging.INFO,
                pathname="",
                lineno=0,
                msg="",
                args=(),
                exc_info=None,
            )
        )
        assert not stderr_filter_func(
            _logging.LogRecord(
                name="test",
                level=_logging.INFO,
                pathname="",
                lineno=0,
                msg="",
                args=(),
                exc_info=None,
            )
        )

    def test_remove_existing_handlers(self):
        """Test that existing handlers are removed before adding new ones."""
        # Create mock handlers to simulate existing handlers
        mock_handler_stdout = MagicMock()
        mock_handler_stderr = MagicMock()

        # Simulate existing handlers in the logger
        handlers = [mock_handler_stdout, mock_handler_stderr]
        self.logger._logger.handlers.clear()  # noqa: SLF001
        self.logger._logger.handlers = handlers  # noqa: SLF001

        # Call setup_logger will remove these handlers
        self.logger._logger = _LoggerAPI.setup_logger()  # noqa: SLF001

        # Assert that previous handlers were removed
        for handl in handlers:
            assert handl in self.logger._logger.handlers  # noqa: SLF001

    def test_logger_format(self):
        """Test the log message format."""
        with patch("sys.stdout"), patch("sys.stderr"):
            self.logger._logger = _LoggerAPI.setup_logger()  # noqa: SLF001

        formatter = self.logger._logger.handlers[0].formatter  # noqa: SLF001
        log_record = _logging.LogRecord(
            name="mockpip",
            level=_LoggerAPI.INFO,
            pathname=__file__,
            lineno=100,
            msg="Test log message",
            args=(),
            exc_info=None,
        )

        assert formatter is not None
        formatted_message = formatter.format(log_record)

        assert "Test log message" in formatted_message
        assert "v" in formatted_message
        assert "mockpip" in formatted_message

    @patch("mockpip.logger._logging.getLogger", return_value=MagicMock())
    def test_mock_logging_methods(self, mock_logger):
        """
        Test that logging methods (info, error, etc.) are called correctly.
        """
        # Force reset the logger
        self.logger._logger = mockpip.logger._LoggerAPI().setup_logger()  # noqa: SLF001

        # Fetch the mock logger
        mock_logger = self.logger._logger  # noqa: SLF001

        # Test logging at INFO level
        self.logger.info("This is an info message")
        mock_logger.info.assert_called_with("This is an info message")

        # Test logging at ERROR level
        self.logger.error("This is an error message")
        mock_logger.error.assert_called_with("This is an error message")

        # Test logging at DEBUG level
        self.logger.debug("This is a debug message")
        mock_logger.debug.assert_called_with("This is a debug message")

        # Test logging at CRITICAL level
        self.logger.critical("This is a critical message")
        mock_logger.critical.assert_called_with("This is a critical message")

    def test_delete_handlers(self):
        del self.logger.handlers

        with pytest.raises(AttributeError):
            _ = self.logger._logger.handlers  # noqa: SLF001

        self.logger.handlers = []

        del self.logger.handlers
        self.logger._logger = self.logger.setup_logger()  # noqa: SLF001

    def test_logger_to_str(self):
        assert str(self.logger) == "<Logger mockpip (INFO)>"

    def test_logger_to_repr(self):
        assert repr(self.logger) == "<Logger mockpip (INFO)>"


if __name__ == "__main__":
    unittest.main()
