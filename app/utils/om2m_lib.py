import requests


class Om2m:
    def __init__(self, XM2MRI, url):
        self.XM2MORIGIN = "SOrigin"
        self.XM2MRI = XM2MRI
        self.url = url

    def create_ae(self, name, labels=[], rr=False):
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
            "X-M2M-Origin": self.XM2MORIGIN + name,
            "Content-Type": "application/json;ty=2",
        }

        r = requests.post(self.url, headers=headers, json=data)
        return r.status_code, r.text

    def create_container(self, name, parent, labels=[], mni=120):
        # Create Node
        data = {"m2m:cnt": {"rn": name, "lbl": labels, "mni": mni}}
        headers = {
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": self.XM2MORIGIN + parent,
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
        data = {"m2m:cin": {"con": con, "lbl": lbl}}

        headers = {
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": self.XM2MORIGIN + parent,
            "Content-Type": "application/json;ty=4",
        }

        r = requests.post(
            self.url + "/" + parent + "/" + node + "/Data?rcn=1",
            headers=headers,
            json=data,
            timeout=timeout,
        )
        return r

    def create_subscription(self, resource_path, rn, nu, exc=10, timeout=None):
        headers = {
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": self.XM2MORIGIN,
            "Content-Type": "application/json;ty=23",
        }
        payload = {
            "m2m:sub": {
                "rn": rn,
                "enc": {"net": ["3"]},
                "nu": [nu],
                "exc": exc,
            }
        }

        r = requests.post(
            f"{self.url}/{resource_path}",
            headers=headers,
            json=payload,
            timeout=timeout,
        )
        return r

    def get_subscription(self, resource_path, timeout=None):
        headers = {
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": self.XM2MORIGIN,
        }
        r = requests.get(
            f"{self.url}/{resource_path}?rcn=1",
            headers=headers,
            timeout=timeout,
        )
        return r

    def delete_subscription(self, resource_path, timeout=None):
        headers = {
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": self.XM2MORIGIN,
        }
        r = requests.delete(
            f"{self.url}/{resource_path}",
            headers=headers,
            timeout=timeout,
        )
        return r

    def delete_resource(self, resource_path, timeout=None):
        print(f"Deleting {resource_path}", "XM2MORIGIN", self.XM2MORIGIN)
        headers = {
            "Accept": "application/json",
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": self.XM2MORIGIN + resource_path.split("/")[0],
        }
        response = requests.delete(
            url=f"{self.url}/{resource_path}?rcn=0",
            headers=headers,
            timeout=timeout,
        )

        return response

    def get_containers(self, resource_path="", ri=None, all=False, timeout=None):
        headers = {
            "Accept": "application/json",
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": self.XM2MORIGIN,
        }
        url = f"{self.url}/{resource_path}"
        if all:
            url = f"{url}?rcn=4"
        response = requests.get(url=url, headers=headers, timeout=timeout)
        return response

    def get_all_resource(self, resource_path: str, timeout=None):
        headers = {
            "Accept": "application/json",
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": self.XM2MORIGIN,
        }
        response = requests.get(
            f"{self.url}/{resource_path}?rcn=4", headers=headers, timeout=timeout
        )
        return response

    def get_la_cin(self, resource_path, timeout=None):
        """
        Gets latest content instance in OM2M.
        """
        headers = {
            "Accept": "application/json",
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": self.XM2MORIGIN,
        }
        print(f"{self.url}/{resource_path}/latest")
        r = requests.get(
            f"{self.url}/{resource_path}/latest",
            headers=headers,
            timeout=timeout,
        )
        return r

    def create_subscription(self, resource_path, rn, nu, nct=2, timeout=None):
        """
        Creates a subscription resource in OM2M.
        """
        data = {"m2m:sub": {"rn": rn, "nu": nu, "nct": nct}}
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
            "Content-Type": "application/json;ty=23",
        }
        r = requests.post(
            f"{self.url}/{resource_path}/Data/",
            headers=headers,
            json=data,
            timeout=timeout,
        )
        return r
