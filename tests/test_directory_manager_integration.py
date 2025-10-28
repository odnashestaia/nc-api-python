def test_directory_exists_check(managers):
    helper = managers["helper"]
    base = managers["base"]

    # подготовка каталога
    assert helper.CreateDirectory("/test_dir")

    d = managers["dirs"]
    assert d.directory_exists_check("/test_dir") is True
    assert d.directory_exists_check("/no_such_dir") in (
        False,
        "Unexpected response: 404 - ",
    )
