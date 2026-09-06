# coding=utf-8
from __future__ import absolute_import

import logging
import os
import json
import io

import octoprint.plugin
import requests
from flask import request, Response

from octoprint.server import admin_permission
from .crealitycloud import CrealityCloud
from .cxhttp import CrealityAPI, CrealityAPIError
class CrealitycloudPlugin(
    octoprint.plugin.StartupPlugin,
    octoprint.plugin.TemplatePlugin,
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.AssetPlugin,
    octoprint.plugin.ProgressPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.BlueprintPlugin,
):
    def __init__(self):
        self._logger = logging.getLogger("octoprint.plugins.crealitycloud")
        self._logger.info(
            "creality cloud init!"
        )
        self.short_code = None
        self._addr = None
        self._regionId = None
        self.printing_befor_connect = True

    def initialize(self):
        self._crealitycloud = CrealityCloud(self)
        self._cxapi = CrealityAPI()

    def get_settings_defaults(self):
        return {
            # put your plugin's default settings here
        }

    ##~~ def on_after_startup(self):
    def on_after_startup(self):
        self._logger.info("creality cloud stared!")
        self._crealitycloud.on_start()

    def on_event(self, event, payload):
        self._crealitycloud.on_event(event, payload)

    ##~~ Softwareupdate hook
    def on_print_progress(self, storage, path, progress):
        self._crealitycloud.on_progress(storage, progress)

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "crealitycloud": {
                "displayName": "Crealitycloud Plugin",
                "displayVersion": self._plugin_version,
                # version check: github repository
                "type": "github_release",
                "user": "crealitycloud",
                "repo": "OctoPrint-CrealityCloud",
                "current": self._plugin_version,
                # update method: pip
                "pip": "https://github.com/msupino/OctoPrint-CrealityCloud/archive/{target_version}.zip",
            }
        }

    def get_template_configs(self):
        return [dict(type="settings", custom_bindings=True)]

    def get_assets(self):
        return dict(
            js=["js/crealitycloud.js"]
        )

    #get token
    @octoprint.plugin.BlueprintPlugin.route("/get_token", methods=["POST"])
    @admin_permission.require(403)
    def get_token(self):
        try:
            data = request.get_json(silent=True) or {}
            token = (data.get("token") or "").strip()
            if not token:
                return {"code": -1, "message": "Missing Creality Cloud token"}

            response = self._cxapi.getconfig(token)
            self._res = response["result"]
            self._config = {               
                "deviceName": self._res["deviceName"],
                "deviceSecret": self._res["tbToken"],
                "iotType": self._res["iotType"],
				"region": self._res["regionId"]
                }
            self._regionId = self._res["regionId"]
            with io.open(
                f"{self.get_plugin_data_folder()}/config.json", "w", encoding="utf-8"
            ) as config_file:
                json.dump(self._config,config_file, indent=2, separators=(',',':'))
                self._logger.debug({
                    "deviceName": self._config.get("deviceName"),
                    "iotType": self._config.get("iotType"),
                    "region": self._config.get("region"),
                    "deviceSecret": "<redacted>",
                })
            self._logger.info("Creality Cloud activation succeeded for region %s", self._res["regionId"])
            return {"code": 0}
        except CrealityAPIError as e:
            self._logger.error("Creality Cloud activation failed: %s", str(e))
            self._logger.error("Creality Cloud activation responses: %s", json.dumps(e.responses))
            return {"code": -1, "message": str(e), "details": e.responses}
        except KeyError as e:
            self._logger.error("Creality Cloud activation response missing field: %s", str(e))
            return {"code": -1, "message": f"Activation response missing field: {e}"}
        except Exception as e:
            self._logger.error(str(e))
            return {"code": -1, "message": str(e)}

    @octoprint.plugin.BlueprintPlugin.route("/snapshot", methods=["GET"])
    def get_snapshot(self):
        snapshot_url = self._settings.global_get(["webcam", "snapshot"])
        if not snapshot_url:
            return {"error": "no webcam configured"}, 404
        try:
            resp = requests.get(snapshot_url, timeout=5)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            return Response(resp.content, mimetype=content_type)
        except Exception as e:
            self._logger.error(f"Snapshot capture failed: {e}")
            return {"error": "snapshot capture failed"}, 502

    @octoprint.plugin.BlueprintPlugin.route("/status", methods=["GET"])
    @admin_permission.require(403)
    def get_status(self):
        country = "US"
        if os.path.exists(f"{self.get_plugin_data_folder()}/config.json"):
            server_region = self._crealitycloud.get_server_region(self._regionId)
            if server_region is not None:
                country = server_region
            if not self._crealitycloud.iot_connected:
                self._logger.info("start iot server")
                self._crealitycloud.device_start()
            return {
                "actived": 1,
                "iot": True,
                "printer": self._printer.is_operational(),
                "country": country,
            }
        else:
            return {"actived": 0, "iot": False, "printer": False, "country": country}

    # get gcode return
    def gCodeHandlerSent(
        self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs
    ):
        if gcode == "M220":
            self._crealitycloud._aliprinter._str_curFeedratePct = cmd

    def gCodeHandlerreceived(self, comm_instance, line, *args, **kwargs):
        if self.printing_befor_connect:
            leftnum = 0
            rightnum = 0
            if not self._crealitycloud._iot_connected:
                return line
            if "SD printing byte " in line:
                self._crealitycloud._aliprinter.mcu_is_print = 1
                self._crealitycloud._aliprinter.state = 1
                leftnum = ""
                rightnum = ""
                percentstr = line.lstrip("SD printing byte ")
                try:
                    leftnum = str(str(percentstr).split('/', 1)[0])
                    rightnum = str(str(percentstr).split('/', 1)[1])
                    self._crealitycloud._aliprinter.printProgress = (float(leftnum) / float(rightnum)) * 100
                except Exception as e:
                    self._logger.error(e)
                
                return line
            elif "Current file: " in line:
                self._crealitycloud._aliprinter.filename = line
                return line
            elif "Not SD printing" in line:
                if (
                        self._crealitycloud._aliprinter.mcu_is_print == 1
                    and not self._crealitycloud._aliprinter.printer.is_printing()
                ):
                    
                    if (
                        not self._crealitycloud._aliprinter.printId
                        and leftnum != 0
                        and rightnum != 0
                        and ((float(leftnum) / float(rightnum)) * 100) > 99.9
                    ):
                        self._crealitycloud._aliprinter.state = 2
                        self._crealitycloud._aliprinter.printProgress = 0
                    else:
                        self._crealitycloud._aliprinter.state = 0
                        self._crealitycloud._aliprinter.printProgress = 0
                    self._crealitycloud._aliprinter.mcu_is_print = 0
                self.printing_befor_connect = False
            return line
        return line


__plugin_name__ = "Crealitycloud Plugin"

__plugin_pythoncompat__ = ">=3,<4"


def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = CrealitycloudPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information,
        "octoprint.comm.protocol.gcode.sent": __plugin_implementation__.gCodeHandlerSent,
        "octoprint.comm.protocol.gcode.received": __plugin_implementation__.gCodeHandlerreceived,
    }
