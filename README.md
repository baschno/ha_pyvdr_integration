# Home Assistant VDR Integration

## Installation
Clone this as `custom_components` into `<user>/homeassistant/.homeassistant/` folder.


## Configuration
Add 
```
sensor:
  - platform: vdr
    host: vdr-local
    port: 6419
    timeout: 2 # (seconds) optional, defaults to 10s
```
to your `configuration.yaml` file.

## Developing

### Install local build
pip install <build-folder>/dist/pyvdr-0.1.2-py3-none-any.whl --upgrade

### Start Home Assistant 
hass --skip-pip
