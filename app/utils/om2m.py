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

    def create_ae(self, name, labels=None, rr=False, timeout=None):
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

        r = requests.post(self.url, headers=headers, json=data, timeout=timeout)
        return r.status_code, r.text

    def create_container(self, name, parent, labels=None, mni=120, timeout=None):
        """
        Creates a container resource in OM2M.
        """
        if labels is None:
            labels = []
        # Create Node
        data = {"m2m:cnt": {"rn": name, "lbl": labels, "mni": mni}}
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
            "Content-Type": "application/json;ty=3",
        }

        r = requests.post(
            f"{self.url}/{parent}", headers=headers, json=data, timeout=timeout
        )

        # Create Data Container inside Node
        data = {"m2m:cnt": {"rn": "Data", "lbl": labels, "mni": mni}}

        r = requests.post(
            f"{self.url}/{parent}/{name}", headers=headers, json=data, timeout=timeout
        )

        return r.status_code

    def create_cin(self, parent, node, con, lbl, cnf, timeout=None):
        """
        Creates a content instance resource in OM2M.
        """
        data = {"m2m:cin": {"con": con, "lbl": lbl, "cnf": cnf}}
        headers = {
            "X-M2M-Origin": f"{self.username}:{self.password}",
            "Content-Type": "application/json;ty=4",
        }
        r = requests.post(
            f"{self.url}/{parent}/{node}/Data",
            headers=headers,
            json=data,
            timeout=timeout,
        )
        return r
