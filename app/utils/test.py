from om2m_lib import Om2m

om2m = Om2m("12345", "http://localhost:8200/Mobius")

resp1 = om2m.create_subscription("ae_test1/cnt_test", "sub1", "http://127.0.0.1:5000")
print(resp1.status_code, resp1.text)

resp2 = om2m.get_subscription("ae_test1/cnt_test/sub1")
print(resp2.status_code, resp2.text)

resp3 = om2m.delete_subscription("ae_test1/cnt_test/sub1")
print(resp3.status_code, resp3.text)