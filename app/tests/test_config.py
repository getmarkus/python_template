from .conftest import settings


def test_testing_database_url():
    """Verify that the database URL is set to sqlite for testing"""
    assert settings.database_url == "sqlite:///./test.db"
    assert settings.current_env == "testing"  # Verify we're in testing environment
