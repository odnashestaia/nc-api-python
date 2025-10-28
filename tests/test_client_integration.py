def test_client_smoke(managers):
    c = managers["client"]
    assert c.dirs and c.files and c.paths and c.users
