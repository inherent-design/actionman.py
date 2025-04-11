# This file tells pytest to ignore this directory when collecting tests


def pytest_ignore_collect(collection_path, config):
    """Tell pytest to ignore this directory when collecting tests."""
    return True
