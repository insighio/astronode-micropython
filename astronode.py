try:
    import ubinascii as binascii
except:
    import binascii
    
from machine import UART # alternative?

import random

try:
    import utime as time
except:
    import time

try:
    import ustruct as struct
except:
    import struct

TIMEOUT_SERIAL = 1500 # ms
BOOT_TIME = 400       # ms

# REQUEST (Asset => Terminal)
CFG_WR = 0x05 # Write configuration, and store in non-volatile memory
WIF_WR = 0x06 # Write Wi-Fi settings, and store non-volatile memory (Wi-Fi only)
SSC_WR = 0x07 # Satellite Search Configuration Write Request. Stored in RAM (never saved in NVM).
CFG_SR = 0x10 # Save configuration in NVM request
CFG_FR = 0x11 # Factory reset configuration request
CFG_RR = 0x15 # Read configuration from non-volatile memory
RTC_RR = 0x17 # Real Time Clock read request
NCO_RR = 0x18 # Next Contact Opportunity read request
MGI_RR = 0x19 # Module GUID read request
MSN_RR = 0x1A # Module Serial Number read request
MPN_RR = 0x1B # Module Product Number read request
PLD_ER = 0x25 # Enqueue uplink payload in non-volatile memory
PLD_DR = 0x26 # Dequeue uplink payload from non-volatile memory
PLD_FR = 0x27 # Clear (Free) all queued payloads from non-volatile memory
GEO_WR = 0x35 # Write geolocation longitude and latitude, and store in non-volatile memory
SAK_RR = 0x45 # Read Acknowledgment
SAK_CR = 0x46 # Confirm to the terminal that Acknowledgment was properly decoded and can be deleted by the terminal
CMD_RR = 0x47 # Read a command message
CMD_CR = 0x48 # Confirm to the module that the command was properly decoded and can be deleted by the module
RES_CR = 0x55 # Clear reset event
TTX_SR = 0x61 # Test Transmit Start Request
EVT_RR = 0x65 # Reads the event register
PER_SR = 0x66 # Context Save Request - recommended before cutting power
PER_RR = 0x67 # Performance Counter Read Request
PER_CR = 0x68 # Performance Counter Clear Request
MST_RR = 0x69 # Module State Read Request
LCD_RR = 0x6A # Last Contact Details Read Request
END_RR = 0x6B # Environment Details Read Request to evaluate RF environment

# ANSWER (Terminal => Asset)
CFG_WA = 0x85 # Answer last configuration write operation with status
WIF_WA = 0x86 # Answer last Wi-Fi settings write operation with status (Wi-Fi only)
SSC_WA = 0x87 # Answer last Satellite Search Configuration write operation
CFG_SA = 0x90 # Answer last configuration save requests with status
CFG_FA = 0x91 # Answer last factory reset request with status
CFG_RA = 0x95 # Answer last configuration read operation with value
RTC_RA = 0x97 # Answer last RTC read request with module time
NCO_RA = 0x98 # Answer with the time to the next contact opportunity
MGI_RA = 0x99 # Answer last GUID read with module GUID
MSN_RA = 0x9A # Answer last Serial Number read with module Serial Number
MPN_RA = 0x9B # Answer last Module Product Number read with the Product Number
PLD_EA = 0xA5 # Answer last uplink payload enqueue operation with status
PLD_DA = 0xA6 # Answer last uplink payload dequeue operation with status
PLD_FA = 0xA7 # Answer last free queued payloads operation with status
GEO_WA = 0xB5 # Answer last geolocation write operation with status
SAK_RA = 0xC5 # Answer with Acknowledgment information
SAK_CA = 0xC6 # Answer last SAK_CR confirmation
CMD_RA = 0xC7 # Answer last CMD_RR with command data
CMD_CA = 0xC8 # Answer last CMD_CR
RES_CA = 0xD5 # Answer the reset clear request
EVT_RA = 0xE5 # Answer indicates which events are currently pending
PER_SA = 0xE6 # Answer confirming Context Save Request
PER_RA = 0xE7 # Answer with Performance Counters in Type, Length, Value format
PER_CA = 0xE8 # Answer confirming Performance Counter Clear Request
MST_RA = 0xE9 # Answer with details of the current Module State
LCD_RA = 0xEA # Answer with details of the Last Contact
END_RA = 0xEB # Answer with details of the RF environment
ERR_RA = 0xFF # Answer a request reporting an error

# Escape characters
STX = b'\x02'
ETX = b'\x03'

# Command/Response size
COMMAND_MAX_SIZE = 200

# Message queue description
ASN_MAX_MSG_SIZE = 160
ASN_MSG_QUEUE_SIZE = 8

# Functions return codes
ANS_STATUS_NONE = 0x0
ANS_STATUS_CRC_NOT_VALID = 0x0001        # Discrepancy between provided CRC and expected CRC.
ANS_STATUS_LENGTH_NOT_VALID = 0x0011,    # Message exceeds the maximum length for a frame.
ANS_STATUS_OPCODE_NOT_VALID = 0x0121     # Invalid Operation Code used.
ANS_STATUS_ARG_NOT_VALID = 0x0122        # Invalid argument used.
ANS_STATUS_FLASH_WRITING_FAILED = 0x0123 # Failed to write to the flash.
ANS_STATUS_DEVICE_BUSY = 0x0124          # Device is busy.
ANS_STATUS_FORMAT_NOT_VALID = 0x0601     # At least one of the fields (SSID, password, token) is not composed of exclusively printable standard ASCII characters (0x20 to 0x7E).
ANS_STATUS_PERIOD_INVALID = 0x0701       # The Satellite Search Config period enumeration value is not valid
ANS_STATUS_BUFFER_FULL = 0x2501          # Failed to queue the payload because the sending queue is already full
ANS_STATUS_DUPLICATE_ID = 0x2511         # Failed to queue the payload because the Payload ID provided by the asset is already in use in the terminal queue.
ANS_STATUS_BUFFER_EMPTY = 0x2601         # Failed to dequeue a payload from the buffer because the buffer is empty
ANS_STATUS_INVALID_POS = 0x3501          # Failed to update the geolocation information. Latitude and longitude fields must in the range [-90,90] degrees and [-180,180] degrees, respectively.
ANS_STATUS_NO_ACK = 0x4501               # No satellite acknowledgement available for any payload.
ANS_STATUS_NO_ACK_CLEAR = 0x4601         # No payload ack to clear, or it was already cleared.
ANS_STATUS_NO_COMMAND = 0x4701           # No command is available.
ANS_STATUS_NO_COMMAND_CLEAR = 0x4801     # No command to clear, or it was already cleared.
ANS_STATUS_MAX_TX_REACHED = 0x6101       # Failed to test Tx due to the maximum number of transmissions being reached.
ANS_STATUS_SUCCESS = 0x7000
ANS_STATUS_TIMEOUT = 0x7001
ANS_STATUS_HW_ERR = 0x7002
ANS_STATUS_DATA_SENT = 0x7003
ANS_STATUS_DATA_RECEIVED = 0x7004
ANS_STATUS_PAYLOAD_TOO_LONG = 0x7005
ANS_STATUS_PAYLOAD_ID_CHECK_FAILED = 0x7006

# Satellite search period
SAT_SEARCH_DEFAULT = 0
SAT_SEARCH_1377_MS = 1
SAT_SEARCH_2755_MS = 2
SAT_SEARCH_4132_MS = 3
SAT_SEARCH_15150_MS = 4
SAT_SEARCH_17905_MS = 5
SAT_SEARCH_23414_MS = 6

# Performance counter types
PER_CMD_LENGTH = 84
PER_TYPE_SAT_SEARCH_PHASE_CNT = 0x01
PER_TYPE_SAT_DETECT_OPERATION_CNT = 0x02
PER_TYPE_SIGNAL_DEMOD_PHASE_CNT = 0x03
PER_TYPE_SIGNAL_DEMOD_ATTEMPS_CNT = 0x04
PER_TYPE_SIGNAL_DEMOD_SUCCESS_CNT = 0x05
PER_TYPE_ACK_DEMOD_ATTEMPT_CNT = 0x06
PER_TYPE_ACK_DEMOD_SUCCESS_CNT = 0x07
PER_TYPE_QUEUED_MSG_CNT = 0x08
PER_TYPE_DEQUEUED_UNACK_MSG_CNT = 0x09
PER_TYPE_ACK_MSG_CNT = 0x0A
PER_TYPE_SENT_FRAGMENT_CNT = 0x0B
PER_TYPE_ACK_FRAGMENT_CNT = 0x0C
PER_TYPE_CMD_DEMOD_ATTEMPT_CNT = 0x0D
PER_TYPE_CMD_DEMOD_SUCCESS_CNT = 0x0E

# Module state types
MST_CMD_LENGTH = 15
MST_TYPE_MSG_IN_QUEUE = 0x41
MST_TYPE_ACK_MSG_QUEUE = 0x42
MST_TYPE_LAST_RST = 0x43
MST_UPTIME = 0x44

# Environment details
END_CMD_LENGTH = 12
END_TYPE_LAST_MAC_RESULT = 0x61
END_TYPE_LAST_SAT_SEARCH_PEAK_RSSI = 0x62
END_TYPE_TIME_SINCE_LAST_SAT_SEARCH = 0x63

# Last contact details
LCD_CMD_LENGTH = 21
LCD_TYPE_TIME_START_LAST_CONTACT = 0x51
LCD_TYPE_TIME_END_LAST_CONTACT = 0x52
LCD_TYPE_PEAK_RSSI_LAST_CONTACT = 0x53
LCD_TYPE_TIME_PEAK_RSSI_LAST_CONTACT = 0x54

# Events
EVENT_MSG_ACK = 1      # A satellite payload acknowledgement is available to be read and confirmed
EVENT_RESET = 2        # Module has reset
EVENT_CMD_RECEIVED = 3 # A command is available to be read and confirmed
EVENT_MSG_PENDING = 4  # An uplink message is present in the message queue, waiting to be sent, and module power should not be cut.
EVENT_NO_EVENT = 0

# Device type
TYPE_ASTRONODE_S = 3
TYPE_WIFI_DEVKIT = 4

# Data commands (downlink)
DATA_CMD_8B_SIZE = 8
DATA_CMD_40B_SIZE = 40

# Astrocast time
ASTROCAST_REF_UNIX_TIME = 1514764800 # 2018-01-01T00:00:00Z (= Astrocast time)

class ASTRONODE:
    def __init__(self, modem_tx=None, modem_rx=None):
        self._serialPort = None
        self._debug_on = False

        if modem_tx is not None and modem_rx is not None:
            self._serialPort = UART(1, 9600, tx=modem_tx, rx=modem_rx)
            self._serialPort.init(9600, bits=8, parity=None, stop=1, tx=modem_tx, rx=modem_rx, timeout=3000, timeout_char=100)

    def _crc16(self, data):
        '''
        CRC-16 (CCITT) implemented with a precomputed lookup table
        '''
        table = [
            0x0000, 0x1021, 0x2042, 0x3063, 0x4084, 0x50A5, 0x60C6, 0x70E7, 0x8108, 0x9129, 0xA14A, 0xB16B, 0xC18C, 0xD1AD, 0xE1CE, 0xF1EF,
            0x1231, 0x0210, 0x3273, 0x2252, 0x52B5, 0x4294, 0x72F7, 0x62D6, 0x9339, 0x8318, 0xB37B, 0xA35A, 0xD3BD, 0xC39C, 0xF3FF, 0xE3DE,
            0x2462, 0x3443, 0x0420, 0x1401, 0x64E6, 0x74C7, 0x44A4, 0x5485, 0xA56A, 0xB54B, 0x8528, 0x9509, 0xE5EE, 0xF5CF, 0xC5AC, 0xD58D,
            0x3653, 0x2672, 0x1611, 0x0630, 0x76D7, 0x66F6, 0x5695, 0x46B4, 0xB75B, 0xA77A, 0x9719, 0x8738, 0xF7DF, 0xE7FE, 0xD79D, 0xC7BC,
            0x48C4, 0x58E5, 0x6886, 0x78A7, 0x0840, 0x1861, 0x2802, 0x3823, 0xC9CC, 0xD9ED, 0xE98E, 0xF9AF, 0x8948, 0x9969, 0xA90A, 0xB92B,
            0x5AF5, 0x4AD4, 0x7AB7, 0x6A96, 0x1A71, 0x0A50, 0x3A33, 0x2A12, 0xDBFD, 0xCBDC, 0xFBBF, 0xEB9E, 0x9B79, 0x8B58, 0xBB3B, 0xAB1A,
            0x6CA6, 0x7C87, 0x4CE4, 0x5CC5, 0x2C22, 0x3C03, 0x0C60, 0x1C41, 0xEDAE, 0xFD8F, 0xCDEC, 0xDDCD, 0xAD2A, 0xBD0B, 0x8D68, 0x9D49,
            0x7E97, 0x6EB6, 0x5ED5, 0x4EF4, 0x3E13, 0x2E32, 0x1E51, 0x0E70, 0xFF9F, 0xEFBE, 0xDFDD, 0xCFFC, 0xBF1B, 0xAF3A, 0x9F59, 0x8F78,
            0x9188, 0x81A9, 0xB1CA, 0xA1EB, 0xD10C, 0xC12D, 0xF14E, 0xE16F, 0x1080, 0x00A1, 0x30C2, 0x20E3, 0x5004, 0x4025, 0x7046, 0x6067,
            0x83B9, 0x9398, 0xA3FB, 0xB3DA, 0xC33D, 0xD31C, 0xE37F, 0xF35E, 0x02B1, 0x1290, 0x22F3, 0x32D2, 0x4235, 0x5214, 0x6277, 0x7256,
            0xB5EA, 0xA5CB, 0x95A8, 0x8589, 0xF56E, 0xE54F, 0xD52C, 0xC50D, 0x34E2, 0x24C3, 0x14A0, 0x0481, 0x7466, 0x6447, 0x5424, 0x4405,
            0xA7DB, 0xB7FA, 0x8799, 0x97B8, 0xE75F, 0xF77E, 0xC71D, 0xD73C, 0x26D3, 0x36F2, 0x0691, 0x16B0, 0x6657, 0x7676, 0x4615, 0x5634,
            0xD94C, 0xC96D, 0xF90E, 0xE92F, 0x99C8, 0x89E9, 0xB98A, 0xA9AB, 0x5844, 0x4865, 0x7806, 0x6827, 0x18C0, 0x08E1, 0x3882, 0x28A3,
            0xCB7D, 0xDB5C, 0xEB3F, 0xFB1E, 0x8BF9, 0x9BD8, 0xABBB, 0xBB9A, 0x4A75, 0x5A54, 0x6A37, 0x7A16, 0x0AF1, 0x1AD0, 0x2AB3, 0x3A92,
            0xFD2E, 0xED0F, 0xDD6C, 0xCD4D, 0xBDAA, 0xAD8B, 0x9DE8, 0x8DC9, 0x7C26, 0x6C07, 0x5C64, 0x4C45, 0x3CA2, 0x2C83, 0x1CE0, 0x0CC1,
            0xEF1F, 0xFF3E, 0xCF5D, 0xDF7C, 0xAF9B, 0xBFBA, 0x8FD9, 0x9FF8, 0x6E17, 0x7E36, 0x4E55, 0x5E74, 0x2E93, 0x3EB2, 0x0ED1, 0x1EF0
        ]

        crc = 0xFFFF
        for byte in data:
            crc = (crc << 8) ^ table[(crc >> 8) ^ byte]
            crc &= 0xFFFF                                   # important, crc must stay 16bits all the way through
        return crc

    def _generate_crc(self, data):
        crc_tmp = '{:04X}'.format(self._crc16(binascii.unhexlify(data)))
        crc = crc_tmp[2]
        crc += crc_tmp[3]
        crc += crc_tmp[0]
        crc += crc_tmp[1]
        return crc

    def ljust(self, byte_array, size):
        byte_array_size = len(byte_array)
        if size > byte_array_size:
            byte_array += b'\x00' * (size - byte_array_size)
        return byte_array

    def text_to_hex(self, text):
        return binascii.hexlify(text).decode('ascii')

    def generate_message(self, payload, include_message_id=False, id=None):
        m = ''
        if include_message_id:
            id = id if id is not None else ('{:04s}'.format((hex(random.randint(0, 65535)))[2:6]))
            m = id
        m += self.text_to_hex(payload)
        return (id, m)

    def generate_geolocation(lat, lng):
        lat_tmp = '{:08x}'.format(int(lat * 1e7) & (2**32-1))
        lng_tmp = '{:08x}'.format(int(lng * 1e7) & (2**32-1))
        geolocation = lat_tmp[6]
        geolocation += lat_tmp[7]
        geolocation += lat_tmp[4]
        geolocation += lat_tmp[5]
        geolocation += lat_tmp[2]
        geolocation += lat_tmp[3]
        geolocation += lat_tmp[0]
        geolocation += lat_tmp[1]
        geolocation += lng_tmp[6]
        geolocation += lng_tmp[7]
        geolocation += lng_tmp[4]
        geolocation += lng_tmp[5]
        geolocation += lng_tmp[2]
        geolocation += lng_tmp[3]
        geolocation += lng_tmp[0]
        geolocation += lng_tmp[1]
        return geolocation

    # Functions prototype
    def encode_send_request(self, opcode, data=""):
        msg = "%0.2X" % opcode
        msg += data
        crc = self._generate_crc(msg)
        msg += crc
        if self._debug_on:
            print(">: {}".format(msg))
        msg = binascii.hexlify(msg.encode())
        msg = self.text_to_hex(STX) + msg.decode()
        msg += self.text_to_hex(ETX)
        msg = binascii.unhexlify(msg)
        msg = msg.upper()

        message_len = self._serialPort.write(msg)
        if message_len is not None:
            return ANS_STATUS_DATA_SENT
        else:
            return ANS_STATUS_HW_ERR

    def receive_decode_answer(self):
        message_buffer = b''
        ret_status = ANS_STATUS_NONE
        opcode = None
        data = None

        start_timestamp = time.ticks_ms()
        timeout_timestamp = start_timestamp + 1000
        do_capture = False
        while True:
            if(time.ticks_ms() >= timeout_timestamp):
                break

            if self._serialPort.any():
                b = self._serialPort.read(1)
                if b == STX:
                    do_capture = True
                    message_buffer = b''

                if do_capture:
                    message_buffer += b

                if b == ETX:
                    break
                continue
            time.sleep_ms(1)

        if self._debug_on:
            print("<: {}".format(message_buffer))

        if len(message_buffer) > 6: # At least STX (1), ETX (1), CRC (4)
            message = message_buffer[1:-5].decode() # [STX (1), - (CRC (4) + ETX (1))]
            cmd_crc_check = message_buffer[-5:-1].decode()
            com_buf_astronode = binascii.unhexlify(message)

            # Verify CRC
            cmd_crc = self._generate_crc(message)

            if cmd_crc == cmd_crc_check:
                if com_buf_astronode[0] == ERR_RA:
                    # Process error code from terminal
                    ret_status = ((com_buf_astronode[2] << 8) + com_buf_astronode[1])
                else:
                    # Extract parameters
                    data = com_buf_astronode[1:]

                    # Return reply from terminal
                    opcode = com_buf_astronode[0]

                    ret_status = ANS_STATUS_DATA_RECEIVED
            else:
                ret_status = ANS_STATUS_CRC_NOT_VALID
        else:
            ret_status = ANS_STATUS_TIMEOUT

        if self._debug_on:
            print("ret_status: {}, opcode: {}, data: {}".format(hex(ret_status), hex(opcode) if opcode is not None else opcode, data))
        return (ret_status, opcode, data)

    def send_cmd(self, reg_req, reg_ans, params=""):
        ret_data = None
        ret_status = self.encode_send_request(reg_req, params)
        if ret_status == ANS_STATUS_DATA_SENT:
            (ret_status, opcode, data) = self.receive_decode_answer()
            if ret_status == ANS_STATUS_DATA_RECEIVED and opcode == reg_ans:
                ret_data = data
        return (ret_status, ret_data)

    def get_error_code_string(code):
        if code == ANS_STATUS_CRC_NOT_VALID:
            return "Discrepancy between provided CRC and expected CRC.\n"
        elif code == ANS_STATUS_LENGTH_NOT_VALID:
            return "Message exceeds the maximum length for a frame.\n"
        elif code == ANS_STATUS_OPCODE_NOT_VALID:
            return "Invalid Operation Code used.\n"
        elif code == ANS_STATUS_ARG_NOT_VALID:
            return "Invalid argument used.\n"
        elif code == ANS_STATUS_FLASH_WRITING_FAILED:
            return "Failed to write to the flash.\n"
        elif code == ANS_STATUS_DEVICE_BUSY:
            return "Device is busy.\n"
        elif code == ANS_STATUS_FORMAT_NOT_VALID:
            return "At least one of the fields (SSID, password, token) is not composed of exclusively printable standard ASCII characters (0x20 to 0x7E).\n"
        elif code == ANS_STATUS_PERIOD_INVALID:
            return "The Satellite Search Config period enumeration value is not valid.\n"
        elif code == ANS_STATUS_BUFFER_FULL:
            return "Failed to queue the payload because the sending queue is already full.\n"
        elif code == ANS_STATUS_DUPLICATE_ID:
            return "Failed to queue the payload because the Payload ID provided by the asset is already in use in the terminal queue.\n"
        elif code == ANS_STATUS_BUFFER_EMPTY:
            return "Failed to dequeue a payload from the buffer because the buffer is empty.\n"
        elif code == ANS_STATUS_INVALID_POS:
            return "Invalid position.\n"
        elif code == ANS_STATUS_NO_ACK:
            return "No satellite acknowledgement available for any payload.\n"
        elif code == ANS_STATUS_NO_ACK_CLEAR:
            return "No payload ack to clear, or it was already cleared.\n"
        elif code == ANS_STATUS_NO_COMMAND:
            return "No command is available.\n"
        elif code == ANS_STATUS_NO_COMMAND_CLEAR:
            return "No command to clear, or it was already cleared.\n"
        elif code == ANS_STATUS_MAX_TX_REACHED:
            return "Failed to test Tx due to the maximum number of transmissions being reached.\n"
        elif code == ANS_STATUS_TIMEOUT:
            return "Failed to receive data from astronode before timeout.\n"
        elif code == ANS_STATUS_HW_ERR:
            return "Failed to send data to the terminal.\n"
        elif code == ANS_STATUS_SUCCESS:
            return ""
        elif code == ANS_STATUS_DATA_SENT:
            return ""
        elif code == ANS_STATUS_DATA_RECEIVED:
            return ""
        else:
            return "Unknown error code.\n"

    class ASTRONODE_CONFIG:
        def __init__(self):
            self.product_id = None
            self.hardware_rev = None
            self.firmware_maj_ver = None
            self.firmware_min_ver = None
            self.firmware_rev = None
            self.with_pl_ack = None
            self.with_geoloc = None
            self.with_ephemeris = None
            self.with_deep_sleep_en = None
            self.with_msg_ack_pin_en = None
            self.with_msg_reset_pin_en = None

    class ASTRONODE_PER_STRUCT:
        def __init__(self):
            self.sat_search_phase_cnt = 0
            self.sat_detect_operation_cnt = 0
            self.signal_demod_phase_cnt = 0
            self.signal_demod_attempt_cnt = 0
            self.signal_demod_success_cnt = 0
            self.ack_demod_attempt_cnt = 0
            self.ack_demod_success_cnt = 0
            self.queued_msg_cnt = 0
            self.dequeued_unack_msg_cnt = 0
            self.ack_msg_cnt = 0
            self.sent_fragment_cnt = 0
            self.ack_fragment_cnt = 0
            self.cmd_demod_attempt_cnt = 0
            self.cmd_demod_success_cnt = 0

    class ASTRONODE_MST_STRUCT:
        def __init__(self):
            self.msg_in_queue = None
            self.ack_msg_in_queue = None
            self.last_rst = None
            self.uptime = None

    class ASTRONODE_END_STRUCT:
        def __init__(self):
            self.last_mac_result = None
            self.last_sat_search_peak_rssi = None
            self.time_since_last_sat_search = None

    class ASTRONODE_LCD_STRUCT:
        def __init__(self):
            self.time_start_last_contact = 0
            self.time_end_last_contact = 0
            self.peak_rssi_last_contact = 0
            self.time_peak_rssi_last_contact = 0

    class ASTRONODE_DOWNLINK_COMMAND_STRUCT:
        def __init__(self):
            self.data = None
            self.create_date = None

    def enableDebugging(self):
        self._debug_on = True

    def disableDebugging(self):
        self._debug_on = False

    def configuration_write(self, with_pl_ack, with_geoloc, with_ephemeris, with_deep_sleep, with_ack_event_pin_mask, with_reset_event_pin_mask):
        # Set parameters
        param_w = bytearray(3)

        if with_pl_ack:
            param_w[0] |= 1 << 0
        if with_geoloc:
            param_w[0] |= 1 << 1
        if with_ephemeris:
            param_w[0] |= 1 << 2
        if with_deep_sleep:
            param_w[0] |= 1 << 3
        if with_ack_event_pin_mask:
            param_w[2] |= 1 << 0
        if with_reset_event_pin_mask:
            param_w[2] |= 1 << 1

        (_, message) = self.generate_message(param_w)

        (status, _) = self.send_cmd(CFG_WR, CFG_WA, message)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def configuration_read(self):
        config = None
        #Send request
        (status, data) = self.send_cmd(CFG_RR, CFG_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            config = ASTRONODE.ASTRONODE_CONFIG()
            config.product_id = data[0]
            config.hardware_rev = data[1]
            config.firmware_maj_ver = data[2]
            config.firmware_min_ver = data[3]
            config.firmware_rev = data[4]
            config.with_pl_ack = (data[5] & (1 << 0))
            config.with_geoloc = (data[5] & (1 << 1))
            config.with_ephemeris = (data[5] & (1 << 2))
            config.with_deep_sleep_en = (data[5] & (1 << 3))
            config.with_msg_ack_pin_en = (data[7] & (1 << 0))
            config.with_msg_reset_pin_en = (data[7] & (1 << 1))

            ret_status = ANS_STATUS_SUCCESS
        return (ret_status, config)

    def configuration_save(self):
        # Send request
        (status, _) = self.send_cmd(CFG_SR, CFG_SA)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def wifi_configuration_write(self, wland_ssid, wland_key, auth_token):
        configuration_wifi = self.ljust(wland_ssid.encode(), 33) + \
                     self.ljust(wland_key.encode(), 64) + self.ljust(auth_token.encode(), 97)

        (_, message) = self.generate_message(configuration_wifi)
        (status, _) = self.send_cmd(WIF_WR, WIF_WA, message)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    # ex:L modem.satellite_search_config_write(astronode.SAT_SEARCH_17905_MS)
    def satellite_search_config_write(self, search_period, force_search=False):
        # Set parameters
        param_w = bytearray(2)

        param_w[0] = struct.pack("B", search_period)[0]
        if force_search:
            param_w[1] |= 1 << 0

        (_, message) = self.generate_message(param_w)

        (status, _) = self.send_cmd(SSC_WR, SSC_WA, message)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def geolocation_write(self, lat, lon):
        # Set parameters
        status = None
        param_w = bytearray()

        param_w += struct.pack("f", lat)
        param_w += struct.pack("f", lon)

        if len(param_w) != 8:
            return status

        (_, message) = self.generate_message(param_w)

        (status, _) = self.send_cmd(GEO_WR, GEO_WA, message)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def factory_reset(self):
        # Send request
        (status, _) = self.send_cmd(CFG_FR, CFG_FA)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def guid_read(self):
        guid = None
        (status, data) = self.send_cmd(MGI_RR, MGI_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            guid = data
            status = ANS_STATUS_SUCCESS
        return (status, guid.decode('ascii').strip().strip('\x00') if guid is not None else None)

    def serial_number_read(self):
        sn = None
        (status, data) = self.send_cmd(MSN_RR, MSN_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            sn = data
            status = ANS_STATUS_SUCCESS
        return (status, sn.decode('ascii').strip().strip('\x00') if sn is not None else None)

    def product_number_read(self):
        pn = None
        (status, data) = self.send_cmd(MPN_RR, MPN_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            pn = data
            status = ANS_STATUS_SUCCESS
        return (status, pn.decode('ascii').strip().strip('\x00') if pn is not None else None)

    def rtc_read(self):
        time = None
        (status, data) = self.send_cmd(RTC_RR, RTC_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            (time_tmp,) = struct.unpack(">L", data)
            time = time_tmp + ASTROCAST_REF_UNIX_TIME
            ret_status = ANS_STATUS_SUCCESS
        return (ret_status, time)

    def read_next_contact_opportunity(self):
        delay = None
        (status, data) = self.send_cmd(RTC_RR, RTC_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            (delay,) = struct.unpack(">L", data)
            ret_status = ANS_STATUS_SUCCESS
        return (ret_status, delay)

    def read_performance_counter(self):
        per_struct = None
        (status, data) = self.send_cmd(PER_RR, PER_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            per_struct = self.ASTRONODE_PER_STRUCT()

            i = 0
            while i < len(data):
                type = data[i]
                length = data[i+1]
                
                if type == PER_TYPE_SAT_SEARCH_PHASE_CNT:
                    (per_struct.sat_search_phase_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_SAT_DETECT_OPERATION_CNT:
                    (per_struct.sat_detect_operation_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_SIGNAL_DEMOD_PHASE_CNT:
                    (per_struct.signal_demod_phase_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_SIGNAL_DEMOD_ATTEMPS_CNT:
                    (per_struct.signal_demod_attempt_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_SIGNAL_DEMOD_SUCCESS_CNT:
                    (per_struct.signal_demod_success_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_ACK_DEMOD_ATTEMPT_CNT:
                    (per_struct.ack_demod_attempt_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_ACK_DEMOD_SUCCESS_CNT:
                    (per_struct.ack_demod_success_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_QUEUED_MSG_CNT:
                    (per_struct.queued_msg_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_DEQUEUED_UNACK_MSG_CNT:
                    (per_struct.dequeued_unack_msg_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_ACK_MSG_CNT:
                    (per_struct.ack_msg_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_SENT_FRAGMENT_CNT:
                    (per_struct.sent_fragment_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_ACK_FRAGMENT_CNT:
                    (per_struct.ack_fragment_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_CMD_DEMOD_ATTEMPT_CNT:
                    (per_struct.cmd_demod_attempt_cnt,) = struct.unpack_from("L", data, i+2)
                elif type == PER_TYPE_CMD_DEMOD_SUCCESS_CNT:
                    (per_struct.cmd_demod_success_cnt,) = struct.unpack_from("L", data, i+2)
                    
                i += (2 + length)
            status = ANS_STATUS_SUCCESS
        
        return (status, per_struct)

    def save_performance_counter(self):
        # Send request
        (status, _) = self.send_cmd(PER_SR, PER_SA)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def clear_performance_counter(self):
        # Send request
        (status, _) = self.send_cmd(PER_CR, PER_CA)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def read_module_state(self):
        module_state = None
        (status, data) = self.send_cmd(MST_RR, MST_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            module_state = self.ASTRONODE_MST_STRUCT()

            i = 0
            while i < len(data):
                type = data[i]
                length = data[i+1]
                
                if type == MST_TYPE_MSG_IN_QUEUE:
                    (module_state.msg_in_queue,) = struct.unpack_from("B", data, i+2)
                elif type == MST_TYPE_ACK_MSG_QUEUE:
                    (module_state.ack_msg_in_queue,) = struct.unpack_from("B", data, i+2)
                elif type == MST_TYPE_LAST_RST:
                    (module_state.last_rst,) = struct.unpack_from("B", data, i+2)
                elif type == MST_UPTIME:
                    (module_state.uptime ,) = struct.unpack_from("L", data, i+2)
                i += (2 + length)
            status = ANS_STATUS_SUCCESS
        
        return (status, module_state)

    def read_environment_details(self):
        env_details = None
        (status, data) = self.send_cmd(END_RR, END_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            env_details = self.ASTRONODE_END_STRUCT()

            i = 0
            while i < len(data):
                type = data[i]
                length = data[i+1]
                
                if type == END_TYPE_LAST_MAC_RESULT:
                    (env_details.last_mac_result,) = struct.unpack_from("B", data, i+2)
                elif type == END_TYPE_LAST_SAT_SEARCH_PEAK_RSSI:
                    (env_details.last_sat_search_peak_rssi,) = struct.unpack_from("B", data, i+2)
                elif type == END_TYPE_TIME_SINCE_LAST_SAT_SEARCH:
                    (env_details.time_since_last_sat_search,) = struct.unpack_from("L", data, i+2)
                i += (2 + length)
            status = ANS_STATUS_SUCCESS
        
        return (status, env_details)

    def read_last_contact_details(self):
        lcd_details = None
        (status, data) = self.send_cmd(END_RR, END_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            lcd_details = self.ASTRONODE_LCD_STRUCT()

            i = 0
            while i < len(data):
                type = data[i]
                length = data[i+1]
                
                if type == LCD_TYPE_TIME_START_LAST_CONTACT:
                    (lcd_details.time_start_last_contact,) = struct.unpack_from("L", data, i+2)
                elif type == LCD_TYPE_TIME_END_LAST_CONTACT:
                    (lcd_details.time_end_last_contact,) = struct.unpack_from("L", data, i+2)
                elif type == LCD_TYPE_PEAK_RSSI_LAST_CONTACT:
                    (lcd_details.peak_rssi_last_contact,) = struct.unpack_from("B", data, i+2)
                elif type == LCD_TYPE_TIME_PEAK_RSSI_LAST_CONTACT:
                    (lcd_details.time_peak_rssi_last_contact,) = struct.unpack_from("L", data, i+2)
                i += (2 + length)
            status = ANS_STATUS_SUCCESS
        
        return (status, lcd_details)

    def enqueue_payload(self, data, id=None):
        status = ANS_STATUS_NONE

        if len(data) <= ASN_MAX_MSG_SIZE:
            # Set parameters
            (message_id, message) = self.generate_message(data, True, id)
            id = message_id
            # Send request
            (status, data) = self.send_cmd(PLD_ER, PLD_EA, message)
            if status == ANS_STATUS_DATA_RECEIVED:
                # Check that enqueued payload has the correct ID
                id_check = binascii.hexlify(data).decode('ascii')
                if id == id_check:
                    status = ANS_STATUS_SUCCESS
                else:
                    status = ANS_STATUS_PAYLOAD_ID_CHECK_FAILED
        else:
            status = ANS_STATUS_PAYLOAD_TOO_LONG

        return (status, id)

    def dequeue_payload(self):
        id = None
        # Send request
        (status, data) = self.send_cmd(PLD_DR, PLD_DA)
        if status == ANS_STATUS_DATA_RECEIVED:
            id = binascii.hexlify(data).decode('ascii')
            status = ANS_STATUS_SUCCESS
        return (status, id)

    def clear_free_payloads(self):
        # Send request
        (status, _) = self.send_cmd(PLD_FR, PLD_FA)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def read_command_8B(self, data, createdDate):
        dl_data = self.ASTRONODE_DOWNLINK_COMMAND_STRUCT()
        (status, data) = self.send_cmd(CMD_RR, CMD_RA)
        if status == ANS_STATUS_DATA_RECEIVED and len(data) == (4+DATA_CMD_8B_SIZE):
            (time_tmp,) = struct.unpack(">L", data)
            dl_data.create_date = time_tmp + ASTROCAST_REF_UNIX_TIME
            dl_data.data = data[4: 4 + DATA_CMD_8B_SIZE]
            ret_status = ANS_STATUS_SUCCESS
        return (ret_status, dl_data)

    def read_command_40B(self, data,createdDate):
        dl_data = self.ASTRONODE_DOWNLINK_COMMAND_STRUCT()
        (status, data) = self.send_cmd(CMD_RR, CMD_RA)
        if status == ANS_STATUS_DATA_RECEIVED and len(data) == (4+DATA_CMD_40B_SIZE):
            (time_tmp,) = struct.unpack(">L", data)
            dl_data.create_date = time_tmp + ASTROCAST_REF_UNIX_TIME
            dl_data.data = data[4: 4 + DATA_CMD_40B_SIZE]
            ret_status = ANS_STATUS_SUCCESS
        return (ret_status, dl_data)

    def clear_command(self):
        # Send request
        (status, _) = self.send_cmd(CMD_CR, CMD_CA)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def event_read(self, event_type):
        event_type = EVENT_NO_EVENT

        #Send request
        (status, data) = self.send_cmd(EVT_RR, EVT_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            if data[0] & (1 << 0):
                event_type = EVENT_MSG_ACK
            elif data[0] & (1 << 1):
                event_type = EVENT_RESET
            elif data[0] & (1 << 2):
                event_type = EVENT_CMD_RECEIVED
            elif data[0] & (1 << 3):
                event_type = EVENT_MSG_PENDING
        return (status, event_type)

    def read_satellite_ack(self):
        id = None
        # Send request
        (status, data) = self.send_cmd(SAK_RR, SAK_RA)
        if status == ANS_STATUS_DATA_RECEIVED:
            id = binascii.hexlify(data).decode('ascii')
            status = ANS_STATUS_SUCCESS
        return (status, id)

    def clear_satellite_ack(self):
        # Send request
        (status, _) = self.send_cmd(SAK_CR, SAK_CA)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def clear_reset_event(self):
        # Send request
        (status, _) = self.send_cmd(RES_CR, RES_CA)
        if status == ANS_STATUS_DATA_RECEIVED:
            status = ANS_STATUS_SUCCESS
        return status

    def is_alive(self):
        (status, _) = self.send_cmd(0x00, 0x00)
        return status == ANS_STATUS_OPCODE_NOT_VALID
