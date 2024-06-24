from fastapi.testclient import TestClient

class CustomTestClient(TestClient):
    def delete_with_payload(self, url, **kwargs):
        return self.request(method="DELETE",url= url, **kwargs)