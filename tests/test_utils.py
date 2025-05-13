import pytest
from unittest.mock import patch, MagicMock
from lambdas.fetch_handler import lambda_handler
import io
import zipfile

@pytest.fixture
def fake_event():
    return {}

def fake_zip_to_test():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w') as zipf:
        zipf.writestr("2m Sales Records.csv", "test...data")
    return buf.getvalue()

@patch("lambdas.fetch_handler.boto3.client")
@patch("lambdas.fetch_handler.urllib3.PoolManager")
def test_lambda_handler(mock_urllib3, mock_boto3, fake_event):
    http = MagicMock()
    http.request.return_value.data = fake_zip_to_test()
    mock_urllib3.return_value = http

    s3 = MagicMock()
    mock_boto3.return_value = s3

    result = lambda_handler(fake_event, {})
    assert result["statusCode"] == 200
    s3.upload_fileobj.assert_called_once()
