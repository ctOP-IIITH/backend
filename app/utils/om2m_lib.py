import requests


class Om2m:
    def __init__(self, XM2MRI, url):
        self.XM2MRI = XM2MRI
        self.url = url

    def create_ae(self, name, labels=[], rr=False):
        XM2MORIGIN = "SOrigin" + name
        data = {
            "m2m:ae": {
                "rn": name,
                "api": "0.2.481.2.0001.001.000111",
                "lbl": labels,
                "rr": rr,
            }
        }
        headers = {
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": XM2MORIGIN,
            "Content-Type": "application/json;ty=2",
        }

        r = requests.post(self.url, headers=headers, json=data)
        return r.status_code, r.text

    def create_container(self, name, parent, labels=[], mni=120):
        XM2MORIGIN = "SOrigin" + parent
        # Create Node
        data = {"m2m:cnt": {"rn": name, "lbl": labels, "mni": mni}}
        headers = {
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": XM2MORIGIN,
            "Content-Type": "application/json;ty=3",
        }

        r = requests.post(self.url + "/" + parent, headers=headers, json=data)

        # Create Data Container inside Node
        data = {"m2m:cnt": {"rn": "Data", "lbl": labels, "mni": mni}}

        r = requests.post(
            self.url + "/" + parent + "/" + name, headers=headers, json=data
        )

        return r

    def create_cin(self, parent, node, con, lbl=None, timeout=None):
        XM2MORIGIN = "SOrigin" + parent
        data = {"m2m:cin": {"con": con, "lbl": lbl}}

        headers = {
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": XM2MORIGIN,
            "Content-Type": "application/json;ty=4",
        }

        r = requests.post(
            self.url + "/" + parent + "/" + node + "/Data?rcn=1",
            headers=headers,
            json=data,
            timeout=timeout,
        )
        return r
