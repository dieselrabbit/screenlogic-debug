# Integration Blueprint

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

_Integration to expose and track over time unconfirmed screenlogicpy data points not exposed by the [built-in ScreenLogic integration][sl_integration]._

**This integration will set up the following platforms.**

| Platform | Description                             |
| -------- | --------------------------------------- |
| `sensor` | Show raw data from the ScreenLogic API. |

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
1. If you do not have a `custom_components` directory (folder) there, you need to create it.
1. In the `custom_components` directory (folder) create a new folder called `screenlogic_debug`.
1. Download _all_ the files from the `custom_components/screenlogic_debug/` directory (folder) in this repository.
1. Place the files you downloaded in the new directory (folder) you created.
1. Restart Home Assistant
1. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Pentair ScreenLogic Debug"

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

---

[sl_integration]: https://www.home-assistant.io/integrations/screenlogic/
[buymecoffee]: https://www.buymeacoffee.com/
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/m/dieselrabbit/screenlogic-debug?style=for-the-badge
[commits]: https://github.com/dieselrabbit/screenlogic-debug/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[discord]: https://discord.gg/Qa5fW2R
[discord-shield]: https://img.shields.io/discord/330944238910963714.svg?style=for-the-badge
[exampleimg]: example.png
[forum-shield]: https://img.shields.io/badge/community-forum-brightgreen.svg?style=for-the-badge
[forum]: https://community.home-assistant.io/
[license-shield]: https://img.shields.io/github/license/dieselrabbit/screenlogic-debug?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/Maintainer-Kevin%20Worrel%20%40dieselrabbit-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/v/release/dieselrabbit/screenlogic-debug?style=for-the-badge
[releases]: https://github.com/dieselrabbit/screenlogic-debug/releases
