# ha-switchbot-curtain
Controls switchbot curtain using Home Assistant

![](../main/switchbot.jpeg)

Supported operations:
  - open / close / stop
  - set position [0-100]%
  - read switchbot sensors / position  

Not supported:
  - password

## Find mac address of your device

### On linux
```
sudo hcitool lescan
```

### In Switchbot app
HOME -> YOUR CURTAIN -> More -> Setting (Top right) -> Three dots (Top right)

## Installation

1. Copy the files of this repository into homeassistant config directory.
2. Add the config to your configuration.yaml file as explained below.
3. Restart Home Assistant

## Config

### Description

  - ```mac``` The MAC address of your curtain.
  - ```name``` (Optional) The name of the Switchbot Curtain.
  - ```reverse``` (Optional, Default: False) Set this to True if your curtain mode is calibrated to 'Open from left to right'.
  - ```time_between_update_command``` (Optional, Default: 10) Time your curtain needs to move from fully closed to fully opened. 
  - ```scan_interval``` (Optional, Default: 3600) Interval Home Assistant updates the states.

### Example
```
cover:
  - platform: switchbot-curtain
    mac: XX:XX:XX:XX:XX:XX
    name: "Curtain living room"
    reverse: True
    time_between_update_command: 11
    scan_interval: 4200
```

## Debugging problems

```
logger:
  default: error
  logs:
    custom_components.switchbot-curtain: debug
```
