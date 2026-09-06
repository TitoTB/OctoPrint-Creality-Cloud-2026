# OctoPrint Plugin for Creality Cloud (2026)

This is a fork from the [original plugin](https://www.crealitycloud.com/es/help-center/how-to-install-cloud-plugin), since the initial method for authentication got deprecated. The plugin has been rebuild to acept current '.tk' files provided by Creality Cloud APP.

The main goal of this fork is to be able to connect non-WiFi printers (such as Ender 3 V3 SE) to Creality Cloud, in order to get points any time you print. No other functionalities have been tested or replicated.

## **Before you start configuring the Plugin:**

You need a [Creality Cloud](https://www.crealitycloud.com/) account to connect OctoPrint and Creality Cloud App.

## **Setup Creality Cloud Plugin on OctoPrint:**

1. Copy the following plugin link.

[https://github.com/TitoTB/OctoPrint-Creality-Cloud-2026/archive/refs/heads/main.zip](https://github.com/TitoTB/OctoPrint-Creality-Cloud-2026/archive/refs/heads/main.zip)

2. Paste and install the plugin link via the bundled "Plugin Manager" on OctoPrint.

![Setup2-1.png](https://cdn.nlark.com/yuque/0/2022/png/22795356/1642471526539-40ed1264-e4d4-41b8-8a58-da74477bb28f.png#clientId=u473873a0-7629-4&crop=0&crop=0&crop=1&crop=1&from=drop&id=ub29fdff4&margin=%5Bobject%20Object%5D&name=Setup2-1.png&originHeight=554&originWidth=700&originalType=binary&ratio=1&rotation=0&showTitle=false&size=80321&status=done&style=none&taskId=u40475215-6d88-4d86-bf78-b11972b0baf&title=)
![Setup2-2.png](https://cdn.nlark.com/yuque/0/2022/png/22795356/1642471535104-1a5bcca0-f2d1-42c1-91ab-efa9dc7d2a64.png#clientId=u473873a0-7629-4&crop=0&crop=0&crop=1&crop=1&from=drop&id=u4ac0df39&margin=%5Bobject%20Object%5D&name=Setup2-2.png&originHeight=613&originWidth=738&originalType=binary&ratio=1&rotation=0&showTitle=false&size=137115&status=done&style=none&taskId=ufd1e6fda-5ce7-4d3f-ba08-0ff07c6508d&title=)

3. Restart the OctoPrint server when you get a prompt.

![Setup3.png](https://cdn.nlark.com/yuque/0/2022/png/22795356/1642471540555-f4bd0b8a-de87-4206-999a-35f7e6da8916.png#clientId=u473873a0-7629-4&crop=0&crop=0&crop=1&crop=1&from=drop&id=u3beba962&margin=%5Bobject%20Object%5D&name=Setup3.png&originHeight=710&originWidth=1088&originalType=binary&ratio=1&rotation=0&showTitle=false&size=158251&status=done&style=none&taskId=uc2f87981-c791-4260-8582-4535f5c8ae5&title=)
## **Generate A Key File in Creality Cloud APP:**

1. Download and open the Creality Cloud APP on your phone, go to Workbench > + > Add Device > Raspberry Pi > Create Raspberry Pi > "Download Key File"
2. Transmit the Key file to your computer.

## **Upload the Key File to OctoPrint:**


Back to the OctoPrint interface on your desktop, click on the OctoPrint setting button > find the "Crealitycloud Plugin" on the left column list > click "Browse" to select and upload the Key file that you transmitted from Creality Cloud APP.

![uploadKey.png](https://cdn.nlark.com/yuque/0/2022/png/22795356/1642471605360-840b996d-5166-4a7d-9212-1ed8f4c08424.png#clientId=u473873a0-7629-4&crop=0&crop=0&crop=1&crop=1&from=drop&id=u60f3a00f&margin=%5Bobject%20Object%5D&name=uploadKey.png&originHeight=813&originWidth=930&originalType=binary&ratio=1&rotation=0&showTitle=false&size=92449&status=done&style=none&taskId=uf1d96ac0-95df-4b59-adb1-726693a1829&title=)
