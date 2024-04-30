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

    def delete_resource(self, resource_path, timeout=None):
        XM2MORIGIN = "SOrigin" + resource_path.split("/")[0]
        print(f"Deleting {resource_path}", "XM2MORIGIN", XM2MORIGIN)
        headers = {
            "Accept": "application/json",
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": XM2MORIGIN,
        }
        response = requests.delete(
            url=f"{self.url}/{resource_path}?rcn=0",
            headers=headers,
            timeout=timeout,
        )

        return response

    def get_containers(self, resource_path="", ri=None, all=False, timeout=None):
        XM2MORIGIN = "SOrigin"
        headers = {
            "Accept": "application/json",
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": XM2MORIGIN,
        }
        url = f"{self.url}/{resource_path}"
        if all:
            url = f"{url}?rcn=4"
        response = requests.get(url=url, headers=headers, timeout=timeout)
        return response

    def get_all_resource(self, resource_path: str, timeout=None):
        XM2MORIGIN = "SOrigin"
        headers = {
            "Accept": "application/json",
            "X-M2M-RI": self.XM2MRI,
            "X-M2M-Origin": XM2MORIGIN,
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
            "X-M2M-Origin": XM2MORIGIN,
        }
        print(f"{self.url}/{resource_path}/latest")
        r = requests.get(
            f"{self.url}/{resource_path}/latest",
            headers=headers,
            timeout=timeout,
        )
        return r
