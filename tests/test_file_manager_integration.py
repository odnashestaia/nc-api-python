def test_file_upload_and_get_data(managers, tmp_path):
    helper = managers["helper"]
    files = managers["files"]

    assert helper.CreateDirectory("/it_dir")

    # upload bytes
    assert files.upload_file(FILE=b"hello", REMOTE_UPLOAD_PATH="/it_dir/a.txt") is True

    # get metadata
    meta = files.get_data_file("/it_dir/a.txt")
    assert meta.get("getetag") is not None


def test_file_download(managers, tmp_path):
    helper = managers["helper"]
    files = managers["files"]

    assert helper.CreateDirectory("/it_dir2")
    assert files.upload_file(FILE=b"world", REMOTE_UPLOAD_PATH="/it_dir2/b.txt") is True

    out = tmp_path / "b.txt"
    assert files.download_file(str(out), "/it_dir2/b.txt") is True
    assert out.read_bytes() == b"world"
