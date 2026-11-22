"""Talk Improv serial to a Speldosa box over USB, as the installer page (ESP Web Tools) does.

    python3 improv_serial_test.py /dev/ttyACM0 info          state, device info, Wi-Fi scan
    python3 improv_serial_test.py /dev/ttyACM0 wifi SECRETS  send Wi-Fi from an ESPHome secrets.yaml
                                                             (wifi_ssid, wifi_password); never printed

Protocol: https://www.improv-wifi.com/serial/ . Packet: "IMPROV", version 1, type, length, data, checksum (sum of
all previous bytes, low byte). Types: 1 current state, 2 error, 3 RPC command, 4 RPC result. RPC data: command,
length, payload. Commands: 1 send Wi-Fi, 2 request state, 3 request device info, 4 request scan.
"""
import re
import sys
import time

import serial

STATES = {1: "authorization required", 2: "authorized (ready)", 3: "provisioning", 4: "provisioned"}
ERRORS = {0: "none", 1: "invalid RPC packet", 2: "unknown RPC command", 3: "unable to connect", 0xFF: "unknown"}


def packet(ptype, data):
    body = b"IMPROV" + bytes([1, ptype, len(data)]) + bytes(data)
    return body + bytes([sum(body) & 0xFF]) + b"\n"


def rpc(cmd, payload=b""):
    return packet(3, bytes([cmd, len(payload)]) + payload)


def read_packets(port, seconds):
    """Collect Improv packets for `seconds`; log text from ESPHome on the same port is skipped."""
    buf, out, end = b"", [], time.time() + seconds
    while time.time() < end:
        buf += port.read(256)
        while (i := buf.find(b"IMPROV")) >= 0 and len(buf) >= i + 9:
            n = buf[i + 8]
            if len(buf) < i + 10 + n:
                break
            pkt = buf[i:i + 10 + n]
            if sum(pkt[:-1]) & 0xFF == pkt[-1]:
                out.append((pkt[7], pkt[9:9 + n]))
            buf = buf[i + 10 + n:]
        buf = buf[-512:]
    return out


def strings(data):
    """RPC result: command, total length, then length-prefixed strings."""
    s, i = [], 2
    while i < len(data):
        n = data[i]; s.append(data[i + 1:i + 1 + n].decode(errors="replace")); i += 1 + n
    return s


def show(pkts):
    for t, d in pkts:
        if t == 1:
            print("state:", STATES.get(d[0], d[0]))
        elif t == 2:
            print("error:", ERRORS.get(d[0], d[0]))
        elif t == 4:
            print(f"rpc result (command {d[0]}):", strings(d))


def main():
    dev, mode = sys.argv[1], sys.argv[2]
    with serial.Serial(dev, 115200, timeout=0.2) as port:
        time.sleep(0.5); port.reset_input_buffer()
        if mode == "info":
            for cmd, wait in ((2, 2), (3, 2), (4, 10)):
                port.write(rpc(cmd)); show(read_packets(port, wait))
        elif mode == "wifi":
            sec = open(sys.argv[3]).read()
            get = lambda k: re.search(rf"^{k}:\s*\"?(.*?)\"?\s*$", sec, re.M).group(1)
            ssid, pw = get("wifi_ssid").encode(), get("wifi_password").encode()
            port.write(rpc(1, bytes([len(ssid)]) + ssid + bytes([len(pw)]) + pw))
            print("Wi-Fi settings sent (SSID and password not shown); waiting up to 30 s")
            show(read_packets(port, 30))


if __name__ == "__main__":
    main()
