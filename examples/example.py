import astronode

try:
    import utime as time
    is_micropython = True
except:
    import time
    is_micropython = False

if is_micropython:
    PIN_TX = 15
    PIN_RX = 16
    modem = astronode.ASTRONODE(15, 16)
else:
    UART_PORT_NAME = "/dev/ttyUSB1"
    modem = astronode.ASTRONODE(None, None, UART_PORT_NAME)

def now_ms():
    if is_micropython:
        return time.ticks_ms()
    else:
        return int(time.time() * 1000)

def sleep_ms(mills):
    if is_micropython:
        time.sleep_ms(mills)
    else:
        time.sleep(mills/1000)

#modem.enableDebugging()

# check if modem is alive
modem_is_alive = False
for x in range(3):
    modem_is_alive = modem.is_alive()
    if modem_is_alive:
        break
    sleep_ms(500)
print("modem is alive: {}".format(modem_is_alive))

# read modem info
(status, pn) = modem.product_number_read()
(status, guid) = modem.guid_read()
(status, sn) = modem.serial_number_read()

print("Product Number: {}".format(pn))
print("GUID: {}".format(guid))
print("S/N: {}".format(sn))

# set WiFi dev kit config
ssid = "<WIFI_SSID>"
password = "<WIFI_PASS>"
token = "<ASTOCAST_PORTAL_ACCESS_TOKEN>"

print("Setting DevKit wifi credentials and access token")
res = modem.wifi_configuration_write(ssid, password, token)

# check modem configuration
(status, config) = modem.configuration_read()
if config.with_pl_ack == 0:
    config.with_pl_ack = 1
    (status, _) = modem.configuration_write(config.with_pl_ack,
                                            config.with_geoloc,
                                            config.with_ephemeris,
                                            config.with_deep_sleep_en,
                                            config.with_msg_ack_pin_en,
                                            config.with_msg_reset_pin_en)
    print("configuration changed successfully: {}".format(status == astronode.ANS_STATUS_SUCCESS))

# send message
(status, message_id) = modem.enqueue_payload(b'\x01\x02')

if status == astronode.ANS_STATUS_BUFFER_FULL:
    print("error: message queue is full, will dequeue and then retry")
    (status, message_id) = modem.dequeue_payload()
    if status == astronode.ANS_STATUS_SUCCESS:
        (status, message_id) = modem.enqueue_payload("test")
        if status != astronode.ANS_STATUS_SUCCESS:
            print("unable to enqueque message, error: {}".format(astronode.get_error_code_string(status)))
            exit

print("Message enqueued with id: {}".format(message_id))

ack_timeout_ms = 3600000 # 1 hour
start_timestamp_ms = now_ms()
end_timestamp_ms = start_timestamp_ms + ack_timeout_ms
while now_ms() < end_timestamp_ms:
    (status, id) = modem.read_satellite_ack()
    if status == astronode.ANS_STATUS_SUCCESS:
        print("ACK received for message with id: {}".format(id))
        (status, id) = modem.clear_satellite_ack()
        if status == astronode.ANS_STATUS_SUCCESS:
            print("ACK cleared")
        break
    print("no ACK received")
    sleep_ms(1000)

    

