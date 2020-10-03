import openapi_python_client.schema as oai

MODULE_NAME = "openapi_python_client.parser.responses"


class TestResponse:
    def test_return_string(self):
        from openapi_python_client.parser.responses import Response

        r = Response(200)

        assert r.return_string() == "None"

    def test_constructor(self):
        from openapi_python_client.parser.responses import Response

        r = Response(200)

        assert r.constructor() == "None"


class TestListRefResponse:
    def test_return_string(self, mocker):
        from openapi_python_client.parser.responses import ListRefResponse

        r = ListRefResponse(200, reference=mocker.MagicMock(class_name="SuperCoolClass"))

        assert r.return_string() == "List[SuperCoolClass]"

    def test_constructor(self, mocker):
        from openapi_python_client.parser.responses import ListRefResponse

        r = ListRefResponse(200, reference=mocker.MagicMock(class_name="SuperCoolClass"))

        assert (
            r.constructor()
            == "[SuperCoolClass.from_dict(item) for item in cast(List[Dict[str, Any]], response.json())]"
        )


class TestRefResponse:
    def test_return_string(self, mocker):
        from openapi_python_client.parser.responses import RefResponse

        r = RefResponse(200, reference=mocker.MagicMock(class_name="SuperCoolClass"))

        assert r.return_string() == "SuperCoolClass"

    def test_constructor(self, mocker):
        from openapi_python_client.parser.responses import RefResponse

        r = RefResponse(200, reference=mocker.MagicMock(class_name="SuperCoolClass"))

        assert r.constructor() == "SuperCoolClass.from_dict(cast(Dict[str, Any], response.json()))"


class TestListBasicResponse:
    def test_return_string(self):
        from openapi_python_client.parser.responses import ListBasicResponse

        r = ListBasicResponse(200, "string")

        assert r.return_string() == "List[str]"

        r = ListBasicResponse(200, "number")

        assert r.return_string() == "List[float]"

        r = ListBasicResponse(200, "integer")

        assert r.return_string() == "List[int]"

        r = ListBasicResponse(200, "boolean")

        assert r.return_string() == "List[bool]"

    def test_constructor(self):
        from openapi_python_client.parser.responses import ListBasicResponse

        r = ListBasicResponse(200, "string")

        assert r.constructor() == "[str(item) for item in cast(List[str], response.json())]"

        r = ListBasicResponse(200, "number")

        assert r.constructor() == "[float(item) for item in cast(List[float], response.json())]"

        r = ListBasicResponse(200, "integer")

        assert r.constructor() == "[int(item) for item in cast(List[int], response.json())]"

        r = ListBasicResponse(200, "boolean")

        assert r.constructor() == "[bool(item) for item in cast(List[bool], response.json())]"


class TestBasicResponse:
    def test_return_string(self):
        from openapi_python_client.parser.responses import BasicResponse

        r = BasicResponse(200, "string")

        assert r.return_string() == "str"

        r = BasicResponse(200, "number")

        assert r.return_string() == "float"

        r = BasicResponse(200, "integer")

        assert r.return_string() == "int"

        r = BasicResponse(200, "boolean")

        assert r.return_string() == "bool"

    def test_constructor(self):
        from openapi_python_client.parser.responses import BasicResponse

        r = BasicResponse(200, "string")

        assert r.constructor() == "str(response.text)"

        r = BasicResponse(200, "number")

        assert r.constructor() == "float(response.text)"

        r = BasicResponse(200, "integer")

        assert r.constructor() == "int(response.text)"

        r = BasicResponse(200, "boolean")

        assert r.constructor() == "bool(response.text)"


class TestBytesResponse:
    def test_return_string(self):
        from openapi_python_client.parser.responses import BytesResponse

        b = BytesResponse(200)

        assert b.return_string() == "bytes"

    def test_constructor(self):
        from openapi_python_client.parser.responses import BytesResponse

        b = BytesResponse(200)

        assert b.constructor() == "bytes(response.content)"


class TestResponseFromData:
    def test_response_from_data_no_content(self, mocker):
        from openapi_python_client.parser.responses import response_from_data

        Response = mocker.patch(f"{MODULE_NAME}.Response")

        status_code = mocker.MagicMock(autospec=int)
        response = response_from_data(status_code=status_code, data=oai.Response.construct())

        Response.assert_called_once_with(status_code=status_code)
        assert response == Response()

    def test_response_from_data_unsupported_content_type(self):
        from openapi_python_client.parser.errors import ParseError
        from openapi_python_client.parser.responses import response_from_data

        content = {"not/real": {}}
        data = oai.Response.construct(content=content)

        assert response_from_data(status_code=200, data=data) == ParseError(
            data=data, detail=f"Unsupported content_type {content}"
        )

    def test_response_from_data_ref(self, mocker):
        ref = mocker.MagicMock()
        status_code = mocker.MagicMock(autospec=int)
        data = oai.Response.construct(
            content={"application/json": oai.MediaType.construct(media_type_schema=oai.Reference.construct(ref=ref))}
        )
        from_ref = mocker.patch(f"{MODULE_NAME}.Reference.from_ref")
        RefResponse = mocker.patch(f"{MODULE_NAME}.RefResponse")
        from openapi_python_client.parser.responses import response_from_data

        response = response_from_data(status_code=status_code, data=data)

        from_ref.assert_called_once_with(ref)
        RefResponse.assert_called_once_with(status_code=status_code, reference=from_ref())
        assert response == RefResponse()

    def test_response_from_data_empty(self, mocker):
        status_code = mocker.MagicMock(autospec=int)
        data = oai.Response.construct()
        Response = mocker.patch(f"{MODULE_NAME}.Response")
        from openapi_python_client.parser.responses import response_from_data

        response = response_from_data(status_code=status_code, data=data)

        Response.assert_called_once_with(status_code=status_code)
        assert response == Response()

    def test_response_from_data_no_response_type(self, mocker):
        status_code = mocker.MagicMock(autospec=int)
        data = oai.Response.construct(
            content={"application/json": oai.MediaType.construct(media_type_schema=oai.Schema.construct(type=None))}
        )
        Response = mocker.patch(f"{MODULE_NAME}.Response")
        from openapi_python_client.parser.responses import response_from_data

        response = response_from_data(status_code=status_code, data=data)

        Response.assert_called_once_with(status_code=status_code)
        assert response == Response()

    def test_response_from_data_array(self, mocker):
        ref = mocker.MagicMock()
        status_code = mocker.MagicMock(autospec=int)
        data = oai.Response.construct(
            content={
                "application/json": oai.MediaType.construct(
                    media_type_schema=oai.Schema.construct(type="array", items=oai.Reference.construct(ref=ref))
                )
            }
        )
        from_ref = mocker.patch(f"{MODULE_NAME}.Reference.from_ref")
        ListRefResponse = mocker.patch(f"{MODULE_NAME}.ListRefResponse")
        from openapi_python_client.parser.responses import response_from_data

        response = response_from_data(status_code=status_code, data=data)

        from_ref.assert_called_once_with(ref)
        ListRefResponse.assert_called_once_with(status_code=status_code, reference=from_ref())
        assert response == ListRefResponse()

    def test_response_from_basic_array(self, mocker):
        status_code = mocker.MagicMock(autospec=int)
        data = oai.Response.construct(
            content={
                "application/json": oai.MediaType.construct(
                    media_type_schema=oai.Schema.construct(type="array", items=oai.Schema.construct(type="string"))
                )
            }
        )
        ListBasicResponse = mocker.patch(f"{MODULE_NAME}.ListBasicResponse")
        from openapi_python_client.parser.responses import response_from_data

        response = response_from_data(status_code=status_code, data=data)

        ListBasicResponse.assert_called_once_with(status_code=status_code, openapi_type="string")
        assert response == ListBasicResponse.return_value

    def test_response_from_data_basic(self, mocker):
        status_code = mocker.MagicMock(autospec=int)
        data = oai.Response.construct(
            content={"text/html": oai.MediaType.construct(media_type_schema=oai.Schema.construct(type="string"))}
        )
        BasicResponse = mocker.patch(f"{MODULE_NAME}.BasicResponse")
        from openapi_python_client.parser.responses import response_from_data

        response = response_from_data(status_code=status_code, data=data)

        BasicResponse.assert_called_once_with(status_code=status_code, openapi_type="string")
        assert response == BasicResponse.return_value

    def test_response_from_dict_unsupported_type(self):
        from openapi_python_client.parser.errors import ParseError
        from openapi_python_client.parser.responses import response_from_data

        data = oai.Response.construct(
            content={"text/html": oai.MediaType.construct(media_type_schema=oai.Schema.construct(type="BLAH"))}
        )

        assert response_from_data(status_code=200, data=data) == ParseError(data=data, detail="Unrecognized type BLAH")

    def test_response_from_data_octet_stream(self, mocker):
        status_code = mocker.MagicMock(autospec=int)
        data = oai.Response.construct(
            content={"application/octet-stream": oai.MediaType.construct(media_type_schema=mocker.MagicMock())}
        )
        BytesResponse = mocker.patch(f"{MODULE_NAME}.BytesResponse")
        from openapi_python_client.parser.responses import response_from_data

        response = response_from_data(status_code=status_code, data=data)

        assert response == BytesResponse()
