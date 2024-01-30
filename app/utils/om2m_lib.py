"""
This module provides a class Om2m to interact with OM2M API.
"""


import requests


class Om2m:
    """
    This class provides methods to interact with OM2M API.
    """

    def __init__(self, username, password, url):
        """
        Initializes the class with username, password and url.
        """
        self.username = username
        self.password = password
        self.url = url

    def create_ae(self, name, path, labels=None, rr=False, timeout=None):
        """
        Creates an Application Entity (AE) resource in OM2M.
        """
        if labels is None:
            labels = []
        data = {"m2m:ae": {"rn": name, "lbl": labels, "rr": rr, "api": name}}
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
            "Content-Type": "application/json;ty=2",
        }

        print(f"{self.url}/{path}", headers, data)
        r = requests.post(
            f"{self.url}/{path}", headers=headers, json=data, timeout=timeout
        )
        print(r.status_code, r.text)
        return r.status_code, r.text

    def create_container(self, name, path, labels=None, mni=120, timeout=None):
        """
        Creates a node resource in OM2M.
        """
        if labels is None:
            labels = []
        data = {"m2m:cnt": {"rn": name, "lbl": labels, "mni": mni}}
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
            "Content-Type": "application/json;ty=3",
        }

        r = requests.post(
            f"{self.url}/{path}", headers=headers, json=data, timeout=timeout
        )
        return r

    def create_cin(self, parent, node, con, lbl=None, timeout=None):
        """
        Creates a content instance resource in OM2M.
        """
        if lbl is None:
            lbl = [node]
        data = {"m2m:cin": {"con": con, "lbl": lbl}}
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
            "Content-Type": "application/json;ty=4",
        }
        url = f"{self.url}/{parent}/{node}"
        if parent == "" or parent is None:
            # Now we have direct ri so we also remove /in-name
            url = self.url.replace("/in-name", "") + f"/{node}"
        print(url, headers, data)
        r = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=timeout,
        )
        return r

    def delete_resource(self, resource_path, timeout=None):
        """
        Deletes a resource in OM2M.
        """
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
        }
        print(f"{self.url}/{resource_path}")
        r = requests.delete(
            f"{self.url}/{resource_path}",
            headers=headers,
            timeout=timeout,
        )
        return r

    def get_containers(self, resource_path="", ri=None, all=False, timeout=None):
        """
        Retrieves all containers from the OM2M server.
        """
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
            "Content-Type": "application/json;ty=3",
        }
        url = f"{self.url}/{resource_path}"
        if ri:
            url = f"{self.url.replace('/in-name', '')}/{ri}"

        if all:
            url = f"{url}?rcn=4"

        r = requests.get(url, headers=headers, timeout=timeout)
        return r

    def get_all_resource(self, resource_path: str, timeout=None):
        """
        Gets all resource in OM2M.
        """
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
        }
        r = requests.get(
            f"{self.url}/{resource_path}?rcn=4",
            headers=headers,
            timeout=timeout,
        )
        return r

    def get_la_cin(self, resource_path, timeout=None):
        """
        Gets latest content instance in OM2M.
        """
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
            "Content-Type": "application/json;ty=4",
        }
        print(f"{self.url}/{resource_path}/la")
        r = requests.get(
            f"{self.url}/{resource_path}/la",
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
            f"{self.url}/{resource_path}",
            headers=headers,
            json=data,
            timeout=timeout,
        )
        return r
