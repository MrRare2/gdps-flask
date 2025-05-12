# GMDprivateServer
## Geometry Dash Private Server Flask ver.
Basically a Geometry Dash Server Emulator but implemented in Python Flask

Supported version of Geometry Dash: 1.0 - 2.2 (i guess)

(See [the backwards compatibility section of this article](https://github.com/Cvolton/GMDprivateServer/wiki/Deliberate-differences-from-real-GD) for more information)

Required programs to run:
Python >= 3.6
Flask >= 3.x

### Setup
1) Upload the files on a webserver
2) Import database.sql into a MySQL/MariaDB database
3) Edit the links in GeometryDash.exe (some are base64 encoded since 2.1, remember that)

#### Updating the server
See [README.md in the `_updates`](_updates/README.md)

### Credits
Base for account settings and the private messaging system by someguy28

Using this for XOR encryption - https://github.com/sathoro/php-xor-cipher - (incl/lib/XORCipher.php)

Using this for cloud save encryption - https://github.com/defuse/php-encryption - (incl/lib/defuse-crypto.phar)

Most of the stuff in generateHash.php has been figured out by pavlukivan and Italian APK Downloader, so credits to them

Using this for base repo - [https://github.com/MegaSa1nt/GMDprivateServer/tree/new](https://github.com/MegaSa1nt/GMDprivateServer/tree/new)
