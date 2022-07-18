# Home Assistant Add-on: Hass-searxng

## What is searxng?

SearXNG is a free internet metasearch engine which aggregates results from various search services and databases. Users are neither tracked nor profiled.

## Installation

Follow these steps to get the add-on installed on your system:

1. Navigate in your Home Assistant frontend to **Supervisor** -> **Add-on Store**.
2. Find the "hass-searxng" add-on and click it.
3. Click on the "INSTALL" button.

## How configure it

In the configuration section, set the port if the default one is not good for you. Enable auth if you want and SSL to.
Even if unused, let the default variables set.

### Addon Configuration

Add-on configuration:

```yaml
certfile: fullchain.pem
keyfile: privkey.pem
```

### Option: `certfile` (required)

The cert of the SSL certificate if the https protocol is provided

### Option: `keyfile` (required)

The private key of the SSL certificate if https enabled

## How to use it ?

Just start the addon and head to the webui at http(s)://host:port (here 8080 by default)

## Useful ressources :

### Documentation

https://docs.searxng.org/
https://github.com/searxng/searxng

## License

This addon is published under the apache 2 license. Original author of the addon's bundled software is searxng
