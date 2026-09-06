import json
import random
import uuid
import base64
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
            "__CXY_OS_LANG_": "1",
            "__CXY_PLATFORM_": "5",
            "__CXY_DUID_": "234",
            "__CXY_APP_ID_": "creality_model",
            "__CXY_APP_VER_": "7.3.20",
            "__CXY_APP_CH_": "google",
            "__CXY_BRAND_": "Raspberry",
            "__CXY_IS_WIFI_": "1",
            "__CXY_TIMEZONE_": "Europe/Madrid",
            "__CXY_REQUESTID_": self._getQrandData(),
        }

    def _getQrandData(self):
        import time

        time = time.localtime(time.time())
        r = random.random() % (99999 - 10000) + 10000
        return f"Raspberry{time.tm_sec}{10}{r}"  # time.tvm_usec

    def _decode_jwt_payload(self, token):
        try:
            payload = token.split(".")[1]
            payload += "=" * (-len(payload) % 4)
            payload = payload.replace("-", "+").replace("_", "/")
            return json.loads(base64.b64decode(payload).decode("utf-8"))
        except Exception:
            return {}

    def _regions_for_token(self, token):
        issuer = self._decode_jwt_payload(token).get("iss", "")

        if "crealitycloud.com" in issuer:
            return (("global", self.__overseaurl),)
        if "crealitycloud.cn" in issuer:
            return (("cn", self.__homeurl),)
        return (("cn", self.__homeurl), ("global", self.__overseaurl))

    def _request_json(self, region, url, data, headers, responses, flow):
        try:
            response = requests.post(url, json=data, headers=headers, timeout=10)
        except requests.RequestException as e:
            responses.append({
                "flow": flow,
                "region": region,
                "url": url,
                "request_body": data,
                "error": str(e),
            })
            return None

        body = response.text
        try:
            parsed = json.loads(body)
        except ValueError:
            parsed = body[:500]

        responses.append({
            "flow": flow,
            "region": region,
            "url": url,
            "request_body": data,
            "status_code": response.status_code,
            "body": parsed,
        })

        if isinstance(parsed, dict) and parsed.get("code") == 0 and parsed.get("result"):
            return parsed
        return None

    def getconfig(self, token, device_name=None):
        token = (token or "").strip()
        if not token:
            raise CrealityAPIError("Missing Creality Cloud token")

        app_headers = dict(self.__headers)
        app_headers.update({
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Origin": "https://www.crealitycloud.com",
            "Referer": "https://www.crealitycloud.com/",
            "User-Agent": "CrealityCloud/7.3.20 (Linux; Android 14)",
        })
        mac=uuid.UUID(int = uuid.getnode()).hex[-12:].upper()
        device_name = (device_name or "").strip()
        responses = []

        for region, base_url in self._regions_for_token(token):
            url = f"{base_url}/api/cxy/v2/device/importDevice"
            data = {"machineCode": token}
            result = self._request_json(region, url, data, app_headers, responses, "apk importDevice machineCode")
            if result:
                return result

        legacy_headers = dict(app_headers)
        legacy_headers.update({
            "__CXY_JWTOKEN_": token,
            "__CXY_TOKEN_": token,
        })
        legacy_data = {"mac": str(mac), "iotType": 2}
        if device_name:
            legacy_data["deviceName"] = device_name

        for region, base_url in self._regions_for_token(token):
            for path in ("/api/cxy/v2/device/importRaspberrypi", "/api/cxy/v2/device/user/importDevice"):
                url = f"{base_url}{path}"
                result = self._request_json(region, url, legacy_data, legacy_headers, responses, "legacy token header")
                if result:
                    return result

        raise CrealityAPIError("Creality Cloud importDevice/importRaspberrypi failed", responses)

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
