from conftest import settings


def test_testing_database_url():
    assert settings.current_env == "testing"  # Verify we're in testing environment
