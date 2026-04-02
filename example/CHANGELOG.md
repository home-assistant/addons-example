<!-- https://developers.home-assistant.io/docs/apps/presentation#keeping-a-changelog -->
## 1.3.1

* Rebuild with updated workflow to include `io.hass.*` labels.
* Remove io.hass.type from Dockerfile, let build add it (with "app" value).

## 1.3.0

- Updated to Alpine 3.23 base image.
- Renamed from "add-on" to "app".

## 1.2.0

- Add an apparmor profile
- Update to 3.15 base image with s6 v3
- Add a sample script to run as service and constrain in aa profile

## 1.1.0

- Updates

## 1.0.0

- Initial release
