import schemathesis
schema = schemathesis.from_path("openapi.yaml")

@schema.parametrize()
def test_api(case):
    case.call_and_validate()