import json
import random
import uuid
import requests


class CrealityAPIError(Exception):
    def __init__(self, message, responses=None):
        super(CrealityAPIError, self).__init__(message)
        self.responses = responses or []


class CrealityAPI(object):
    def __init__(self):
        self.__homeurl = "https://api.crealitycloud.cn"
        self.__overseaurl = "https://api.crealitycloud.com"
        self.__headers = {
            "__CXY_OS_VER_": "v0.0.1",
            "_CXY_OS_LANG_": "1",
            "__CXY_PLATFORM_": "5",
            "__CXY_DUID_": "234",
            "__CXY_APP_ID_": "creality_model",
            "__CXY_REQUESTID_": self._getQrandData(),
        }

    def _getQrandData(self):
        import time

        time = time.localtime(time.time())
        r = random.random() % (99999 - 10000) + 10000
        return f"Raspberry{time.tm_sec}{10}{r}"  # time.tvm_usec

    def getconfig(self, token):
        home_url = f"{self.__homeurl}/api/cxy/v2/device/user/importDevice"
        oversea_url = f"{self.__overseaurl}/api/cxy/v2/device/user/importDevice"
        token = (token or "").strip()
        if not token:
            raise CrealityAPIError("Missing Creality Cloud token")

        headers = {
            "Content-Type": "application/json",
            "__CXY_JWTOKEN_": token
        }
        mac=uuid.UUID(int = uuid.getnode()).hex[-12:].upper()
        data = f'{{"mac": "{mac}" , "iotType": 2}}'
        responses = []

        for region, url in (("cn", home_url), ("global", oversea_url)):
            try:
                response = requests.post(url, data=data, headers=headers, timeout=5)
            except requests.RequestException as e:
                responses.append({
                    "region": region,
                    "url": url,
                    "error": str(e),
                })
                continue

            body = response.text
            try:
                parsed = json.loads(body)
            except ValueError:
                parsed = body[:500]

            responses.append({
                "region": region,
                "url": url,
                "status_code": response.status_code,
                "body": parsed,
            })

            if isinstance(parsed, dict) and parsed.get("code") == 0 and parsed.get("result"):
                return parsed

        raise CrealityAPIError("Creality Cloud importDevice failed", responses)

    def getAddrress1(self):
        url = f"{self.__homeurl}/api/cxy/v2/common/getAddrress"
        response = requests.post(url, data="{}", headers=self.__headers, timeout=5).text
        res = json.loads(response)
        if res["code"] == 0:
            if res["result"]["apiUrl"] != None:
                return (res["result"]["apiUrl"], res["result"]["country"])
        return ("", "US")

    def getAddrress2(self):
        url = f"{self.__overseaurl}/api/cxy/v2/common/getAddrress"
        response = requests.post(url, data="{}", headers=self.__headers, timeout=5).text
        res = json.loads(response)
        if res["code"] == 0:
            if res["result"]["apiUrl"] != None:
                return (res["result"]["apiUrl"], res["result"]["country"])
        return ("", "US")

    def exchangeTb(self, deviceName, productKey, deviceSecret, region):
        homeurl = f"{self.__homeurl}/api/cxy/v2/device/user/exchangeTb"
        overseaurl = f"{self.__overseaurl}/api/cxy/v2/device/user/exchangeTb"
        data = f'{{"deviceName": "{deviceName}" , "productKey": "{productKey}" , "deviceSecret": "{deviceSecret}"}}'
        headers = {
            "Content-Type": "application/json",
        }
        if region == 0:
            url = homeurl
        else :
            url = overseaurl
        response = requests.post(url, data=data, headers=headers, timeout=5).text
        res = json.loads(response)
        return res
