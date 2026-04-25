from inscrawler.fetch import get_parsed_hashtags, get_parsed_mentions


class TestGetParsedMentions:
    def test_single_mention(self):
        assert get_parsed_mentions("Hello @user1") == ["user1"]

    def test_multiple_mentions(self):
        result = get_parsed_mentions("Hey @alice and @bob.smith!")
        assert result == ["alice", "bob.smith"]

    def test_no_mentions(self):
        assert get_parsed_mentions("No mentions here") == []

    def test_empty_string(self):
        assert get_parsed_mentions("") == []

    def test_mention_with_dot(self):
        assert get_parsed_mentions("Follow @john.doe") == ["john.doe"]

    def test_mention_at_start(self):
        assert get_parsed_mentions("@user posted something") == ["user"]


class TestGetParsedHashtags:
    def test_single_hashtag(self):
        assert get_parsed_hashtags("#python") == ["python"]

    def test_multiple_hashtags(self):
        result = get_parsed_hashtags("Loving #python and #coding today")
        assert result == ["python", "coding"]

    def test_no_hashtags(self):
        assert get_parsed_hashtags("No hashtags here") == []

    def test_empty_string(self):
        assert get_parsed_hashtags("") == []

    def test_hashtag_at_start(self):
        assert get_parsed_hashtags("#travel is amazing") == ["travel"]

    def test_mixed_content(self):
        result = get_parsed_hashtags("@user loves #travel and #food!")
        assert result == ["travel", "food"]
