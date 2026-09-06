/*
 * View model for OctoPrint-Crealitycloud
 *
 * Author: hemiao & xiongrui
 * License: AGPLv3
 */
$(function () {
  function CrealitycloudViewModel(parameters) {
    var self = this;
    self.isAcitived = ko.observable(false);
    self.activedMsg = ko.observable("");
    self.appdownloadUrl = ko.observable("");
    // assign the injected parameters, e.g.:
    
    // TODO: Implement your plugin's view model here.

    self.formatActivationDetails = function (details) {
      if (!details || !details.length) {
        return "";
      }

      return details.map(function (item) {
        var parts = [item.region || "unknown"];
        if (item.status_code) {
          parts.push("HTTP " + item.status_code);
        }
        if (item.error) {
          parts.push(item.error);
        }
        if (item.body) {
          if (typeof item.body === "string") {
            parts.push(item.body);
          } else {
            parts.push(JSON.stringify(item.body));
          }
        }
        return parts.join(": ");
      }).join("\n");
    };

    self.extractTokenAndDeviceName = function (rawToken) {
      var text = (rawToken || "").trim();
      var result = {
        token: text,
        deviceName: (document.getElementById("manual_device_name_input").value || "").trim()
      };

      text.split(/\r?\n/).forEach(function (line) {
        var cleaned = line.trim();
        if (cleaned.indexOf("DN:") === 0 && !result.deviceName) {
          result.deviceName = cleaned.slice(3).trim();
        } else if (cleaned.split(".").length === 3) {
          result.token = cleaned;
        }
      });

      return result;
    };

    self.submitToken = function (token) {
      var activation = self.extractTokenAndDeviceName(token);
      token = activation.token;
      token = (token || "").trim();
      if (!token) {
        alert("Please provide a Creality Cloud token.");
        return;
      }

      $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: PLUGIN_BASEURL + "crealitycloud/get_token",
        data: JSON.stringify({ token: token, deviceName: activation.deviceName }),
        dataType: "json",
        success: function (data) {
          if (data.code == 0){
            self.isAcitived(true);
            self.getStatus(true)
          }else{
            var message = data.message || "Fail to install the device due to an invalid token. Please download again or regenerate the Key file.";
            var details = self.formatActivationDetails(data.details);
            alert(message + (details ? "\n\n" + details : "") + "\n\nCheck octoprint.log for the full Creality Cloud response.");
          }
        },
        error: function (xhr) {
          alert("Creality Cloud activation request failed. Check octoprint.log for details.");
        }
      });
    };

    document.getElementById("token_file_input").addEventListener("change",function () {
      var selectedFile = document.getElementById('token_file_input').files[0];
      var reader = new FileReader();
      reader.readAsText(selectedFile);
      reader.onload = function(){
        self.submitToken(this.result);
      }
    });

    document.getElementById("manual_token_submit").addEventListener("click", function () {
      self.submitToken(document.getElementById("manual_token_input").value);
    });

    self.saveManualConfig = function () {
      var config = (document.getElementById("manual_config_input").value || "").trim();
      if (!config) {
        alert("Please paste the Creality Cloud activation JSON.");
        return;
      }

      $.ajax({
        type: "POST",
        contentType: "application/json; charset=utf-8",
        url: PLUGIN_BASEURL + "crealitycloud/save_config",
        data: JSON.stringify({ config: config }),
        dataType: "json",
        success: function (data) {
          if (data.code == 0) {
            self.isAcitived(true);
            self.getStatus(true);
          } else {
            alert(data.message || "Could not save the manual Creality Cloud config.");
          }
        },
        error: function () {
          alert("Manual config save request failed. Check octoprint.log for details.");
        }
      });
    };

    document.getElementById("manual_config_submit").addEventListener("click", self.saveManualConfig);

    self.openCrealityCloud = function () {
      window.open("http://www.crealitycloud.com");
    };
    self.getStatus = function (bInit) {
      $.ajax({
        type: "GET",
        contentType: "application/json; charset=utf-8",
        url: PLUGIN_BASEURL + "crealitycloud/status",
        data: {},
        dataType: "json",
        success: function (data) {
          if (data.actived == 1) {
            self.isAcitived(true);
            self.activedMsg("Raspberry Pi has been activated on the " + data.country + " server")
            self.HAS_WAIT_TIMEOUT = self.WAIT_TIMEOUT
          } else {
            self.isAcitived(false);
          }
          if (bInit) {
            if (data.country == "China") {
              self.appdownloadUrl("https://www.crealitycloud.cn")
              $("#region").val("China")
            } else {
              self.appdownloadUrl("https://www.crealitycloud.com")
              $("#region").val("US")
            }

          }
        }
      })
    };

    self.getStatus(true);

  }

  /* view model class, parameters for constructor, container to bind to
   * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
   * and a full list of the available options.
   */
  OCTOPRINT_VIEWMODELS.push({
    construct: CrealitycloudViewModel,
    // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
    dependencies: ["settingsViewModel", "loginStateViewModel"],
    // Elements to bind to, e.g. #settings_plugin_crealitycloud, #tab_plugin_crealitycloud, ...
    elements: ["#settings_plugin_crealitycloud"]
  });
});
