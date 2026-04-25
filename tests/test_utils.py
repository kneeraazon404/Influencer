from unittest.mock import patch

import pytest

from inscrawler.exceptions import RetryException
from inscrawler.utils import instagram_int, randmized_sleep, retry, validate_posts


class TestInstagramInt:
    def test_plain_number(self):
        assert instagram_int("1000") == 1000

    def test_comma_separated(self):
        assert instagram_int("1,234") == 1234

    def test_large_number(self):
        assert instagram_int("1,234,567") == 1234567

    def test_zero(self):
        assert instagram_int("0") == 0


class TestRandomizedSleep:
    def test_sleep_called_within_range(self):
        average = 2
        calls = []
        with patch("inscrawler.utils.sleep", side_effect=calls.append):
            randmized_sleep(average)
        assert len(calls) == 1
        assert average * 0.5 <= calls[0] <= average * 1.5

    def test_default_average(self):
        calls = []
        with patch("inscrawler.utils.sleep", side_effect=calls.append):
            randmized_sleep(1)
        assert 0.5 <= calls[0] <= 1.5


class TestRetryDecorator:
    def test_succeeds_on_first_attempt(self):
        counter = {"n": 0}

        @retry(attempt=3)
        def fn():
            counter["n"] += 1

        fn()
        assert counter["n"] == 1

    def test_retries_on_retry_exception(self):
        counter = {"n": 0}

        @retry(attempt=3, wait=0)
        def fn():
            counter["n"] += 1
            if counter["n"] < 3:
                raise RetryException()

        fn()
        assert counter["n"] == 3

    def test_raises_after_max_attempts(self):
        @retry(attempt=2, wait=0)
        def fn():
            raise RetryException()

        with pytest.raises(RetryException):
            fn()


class TestValidatePosts:
    def test_unique_datetimes(self, capsys):
        posts = {
            "a": {"datetime": "2024-01-01"},
            "b": {"datetime": "2024-01-02"},
        }
        validate_posts(posts)
        captured = capsys.readouterr()
        assert "correct" in captured.out

    def test_duplicate_datetimes(self, capsys):
        posts = {
            "a": {"datetime": "2024-01-01"},
            "b": {"datetime": "2024-01-01"},
        }
        validate_posts(posts)
        captured = capsys.readouterr()
        assert captured.out == ""
