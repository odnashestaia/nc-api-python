def test_rename_and_delete(managers):
    helper = managers["helper"]
    files = managers["files"]
    paths = managers["paths"]

    assert helper.CreateDirectory("/itp")
    assert files.upload_file(FILE=b"x", REMOTE_UPLOAD_PATH="/itp/x.txt") is True

    assert paths.rename_path("/itp/x.txt", "/itp/y.txt") is True
    assert paths.delete_path("/itp/y.txt")
