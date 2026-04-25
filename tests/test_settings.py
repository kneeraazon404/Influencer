import argparse

from inscrawler.settings import (
    defaults,
    override_settings,
    prepare_override_settings,
    settings,
)


class TestDefaults:
    def test_all_defaults_false(self):
        for key in defaults:
            assert getattr(settings, key) is False

    def test_default_keys_present(self):
        expected = {
            "fetch_likes_plays",
            "fetch_likers",
            "fetch_comments",
            "fetch_mentions",
            "fetch_hashtags",
            "fetch_details",
        }
        assert set(defaults.keys()) == expected


class TestOverrideSettings:
    def setup_method(self):
        for key in defaults:
            setattr(settings, key, False)

    def test_override_single_flag(self):
        parser = argparse.ArgumentParser()
        prepare_override_settings(parser)
        args = parser.parse_args(["--fetch_comments"])
        override_settings(args)
        assert settings.fetch_comments is True
        assert settings.fetch_likes_plays is False

    def test_override_multiple_flags(self):
        parser = argparse.ArgumentParser()
        prepare_override_settings(parser)
        args = parser.parse_args(["--fetch_comments", "--fetch_hashtags"])
        override_settings(args)
        assert settings.fetch_comments is True
        assert settings.fetch_hashtags is True
        assert settings.fetch_mentions is False

    def test_no_flags_keeps_defaults(self):
        parser = argparse.ArgumentParser()
        prepare_override_settings(parser)
        args = parser.parse_args([])
        override_settings(args)
        for key in defaults:
            assert getattr(settings, key) is False


class TestPrepareOverrideSettings:
    def test_all_flags_registered(self):
        parser = argparse.ArgumentParser()
        prepare_override_settings(parser)
        for key in defaults:
            args = parser.parse_args([f"--{key}"])
            assert getattr(args, key) is True
