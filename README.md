# astronode-micropython
python / micropython library for the Astronode S

This library is a direct port to micropython of Astrocast's official Arduino library: https://github.com/Astrocast/astronode-arduino-library

# Tested boards / Environments
* ESP32
* ESP8266
* Ubuntu
* Windows

# API reference

The implementation of [Astronode's Serial Commands Definition](https://docs.astrocast.com/docs/products/astronode-api/commands-definition). 



## class `ASTRONODE`: 
The main class that handles the module commands:
  ### `__init__(module_tx, module_rx, module_serial_port_name)`
  Constructor of the class
  * Parameters:
    * `module_tx`: the UART TX Pin number/name (in __micropython__). Else in __Python__, `None`
    * `module_rx`: the UART RX Pin number/name (in __micropython__). Else in __Python__, `None`
    * `module_serial_port_name`: `None` (in __micropython__). Else in __Python__ the name of the UART (ex. in Linux `/dev/ttyUSB0`, in Windows `COM3`)

  ### class `ASTRONODE_CONFIG`
  Class for module configuration storage. 
  * `product_id`
  * `hardware_rev`
  * `firmware_maj_ver`
  * `firmware_min_ver`
  * `firmware_rev`
  * `with_pl_ack`
  * `with_geoloc`
  * `with_ephemeris`
  * `with_deep_sleep_en`
  * `with_msg_ack_pin_en`
  * `with_msg_reset_pin_en`

  ### class `ASTRONODE_PER_STRUCT`
  Class for storing Performance Counters
  * `sat_search_phase_cnt`
  * `sat_detect_operation_cnt`
  * `signal_demod_phase_cnt`
  * `signal_demod_attempt_cnt`
  * `signal_demod_success_cnt`
  * `ack_demod_attempt_cnt`
  * `ack_demod_success_cnt`
  * `queued_msg_cnt`
  * `dequeued_unack_msg_cnt`
  * `ack_msg_cnt`
  * `sent_fragment_cnt`
  * `ack_fragment_cnt`
  * `cmd_demod_attempt_cnt`
  * `cmd_demod_success_cnt`

  ### class `ASTRONODE_MST_STRUCT`
  Class for storing Module State
  * `msg_in_queue`
  * `ack_msg_in_queue`
  * `last_rst`
  * `uptime`

  ### class `ASTRONODE_END_STRUCT`
  Class for storing Environment Details 
  * `last_mac_result`
  * `last_sat_search_peak_rssi`
  * `time_since_last_sat_search`

  ### class `ASTRONODE_LCD_STRUCT`
  Class for storing Last Contact Details
  * `time_start_last_contact`
  * `time_end_last_contact`
  * `peak_rssi_last_contact`
  * `time_peak_rssi_last_contact`

  ### class `ASTRONODE_DOWNLINK_COMMAND_STRUCT`
  Class for storing Downling Command Info
  * `create_date`
  * `data`

  ### `is_alive()`
  Check connectivity with the module.
  * Returns:
    * (boolean) the connection status with the module.

  ### `send_cmd(reg_req, reg_ans, params)`
  Send command, validate response code and get response data
  * Parameters:
    * `reg_req`: (int) the code of the request command as defined in Astrocast's documentation
    * `reg_ans`: (int) the code of the expected response command as defined in Astrocast's documentation
    * `params`: (string / bytearray) the parameters of the request command. Strings can be accepted, otherwise it is advised to provide bytearrays (ex. b'testing')
  * Returns tuple (status, data):
    * `status`: (int) the status code of the operation. Possible values are defined as macros at `astronode.ANS_STATUS_*`. A successful call always returns `astronode.ANS_STATUS_DATA_RECEIVED`. Can be translated into human readable form by calling [ASTRONODE.get_error_code_string(status)](#get_error_code_stringcode)
    * `data`: (bytearray) the data in bytes returned by the module. They require further processing to be usable.
      
  ### `get_error_code_string(code)`
  Get a human readable description for the return status of the commands
  * Parameters:
    * `code`: the status code to be translated
  * Returns:
    * `text`: (string) the description of the code
      
  ### `enableDebugging()`
  Enable debug printing
  
  ### `disableDebugging()`
  Disable debug printing
  
  ### `configuration_write`(`with_pl_ack`, `with_geoloc`, `with_ephemeris`, `with_deep_sleep`, `with_ack_event_pin_mask`, `with_reset_event_pin_mask`)`
  Setup the behavior of the module (link: [CFG_WR Request](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#cfg_wr-request)):
  * Parameters:
    * `with_pl_ack`: Enable Satellite Acknowledgement Notification
    * `with_geoloc`: Add Geolocation data to message (see: `ASTRONODE.geolocation_write`)
    * `with_ephemeris`: Enable Ephemeris
    * `with_deep_sleep`: Enable Deep Sleep Mode
    * `with_ack_event_pin_mask`: Enable Payload Ack Event Pin Mask
    * `with_reset_event_pin_mask`: Enable Reset Notification Event Pin Mask
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `configuration_read()`
  Read the device configuration (link: [CFG_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#cfg_rr-request))
  * Returns tuple (status, config):
    * `status`: (int) the status code of the operation
    * `config`: [ASTRONODE.ASTRONODE_CONFIG](#class-astronode_config) object

  ### `configuration_save()`
  Save the current configuration (link: [CFG_SR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#cfg_sr-request))
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `wifi_configuration_write`(`wlan_ssid`, `wlan_key`, `auth_token`)
  When using WiFi Dev Kit, set WiFi credentials and Astrocast Portal Access Token (link: [WIF_WR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#wif_wr-request))
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `satellite_search_config_write`(`search_period`, `force_search`)
  Set Satellite Search Configuration (link: [SSC_WR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#ssc_wr-request))
  * Parameters:
    * `search_period`: Search Period Enumeration defined as macro astronode.SAT_SEARCH_*
    * `force_search`: Enable search without message queued
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `geolocation_write`(`lat`, `lon`)
  Set device geolocation info to be send if [ASTRONODE.ASTRONODE_CONFIG](#class-astronode_config)`.with_geoloc` is enabled (link: [GEO_WR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#geo_wr-request))
  * Parameters:
    * `lat`: (float) Latitude value
    * `lon`: (float) Longitude value
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `factory_reset()`
  Factory reset module (link: [CFG_FR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#cfg_fr-request))
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `guid_read()`
  Read Module GUID (link: [MGI_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#mgi_rr-request))
  * Returns tuple (status, guid):
    * `status`: (int) the status code of the operation
    * `guid`: (string) Module's GUID

  ### `serial_number_read()`
  Read Module Serial Number (link: [MSN_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#msn_rr-request))
  * Returns tuple (status, sn):
    * `status`: (int) the status code of the operation
    * `sn`: (string) modules's Serial Number

  ### `product_number_read()`
  Read Module Product Number (link: [MPN_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#mpn_rr-request))
  * Returns tuple (status, pn):
    * `status`: (int) the status code of the operation
    * `pn`: (string) modules's Product Number

  ### `rtc_read()`
  Read Modules GUID (link: [RTC_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#rtc_rr-request))
  * Returns tuple (status, time):
    * `status`: (int) the status code of the operation
    * `time`: (int) rtc time in epoch

  ### `read_next_contact_opportunity()`
  Read Next Contact Opportunity (link: [NCO_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#nco_rr-request))
  * Returns tuple (status, time):
    * `status`: (int) the status code of the operation
    * `time`: (int) time in seconds until the start of the next pass opportunity

  ### `read_performance_counter()`
  Read Performance Counters (link: [PER_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#per_rr-request))
  * Returns tuple (status, per_data):
    * `status`: (int) the status code of the operation
    * `per_data`: [ASTRONODE.ASTRONODE_PER_STRUCT](#class-astronode_per_struct) object

  ### `save_context()`
  Save the current context to NVM (link: [CTX_SR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#ctx_s-context-save))
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `clear_performance_counter()`
  Reset the performance counters to zero (link: [PER_CR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#per_cr-request))
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `read_module_state()`
  Get information about the message queue and the last reset reason (link: [MST_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#mst_r-module-state-read))
  * Returns tuple (status, module_state):
    * `status`: (int) the status code of the operation
    * `module_state`: [ASTRONODE.ASTRONODE_MST_STRUCT](#class-astronode_mst_struct) object

  ### `read_environment_details()`
  Get environment details (link: [END_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#end_r-environment-details-read))
  * Returns tuple (status, env_details):
    * `status`: (int) the status code of the operation
    * `env_details`: [ASTRONODE.ASTRONODE_END_STRUCT](#class-astronode_end_struct) object

  ### `read_last_contact_details()`
  Get environment details (link: [LCD_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#lcd_r-last-contact-details-read))
  * Returns tuple (status, lcd_details):
    * `status`: (int) the status code of the operation
    * `lcd_details`: [ASTRONODE.ASTRONODE_LCD_STRUCT](#class-astronode_lcd_struct) object

  ### `enqueue_payload`(`data`, `id`)
  Place a payload in the module queue. (link: [PLD_ER](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#pld_e-enqueue-payload))
  * Parameters:
    * `data`: (bytearray) the payload in bytes to be transmitted (max: 160 bytes). 
    * `id`: (2 bytes) ID of the message. If omitted, an auto-generated ID will be used.
  * Returns tuple (status, id):
    * `status`: (int) the status code of the operation
    * `id`: (2 bytes) the ID of the message
  
  ### `dequeue_payload()`
  Remove the oldest payload from the module queue. (link: [PLD_DR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#pld_d-dequeue-payload))
  * Returns tuple (status, id):
    * `status`: (int) the status code of the operation
    * `id`: (2 bytes) the ID of the message

  ### `clear_free_payloads()`
  Clean pending payload queue. (link: [PLD_FR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#pld_f-clearfree-payloads))
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `read_command()`
  Read downlink command. (link: [CMD_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#cmd_r-command-read))
  * Returns tuple (status, dl_data):
    * `status`: (int) the status code of the operation
    * `dl_data`: instance of [ASTRONODE.ASTRONODE_DOWNLINK_COMMAND_STRUCT](#class-astronode_downlink_command_struct)

  ### `clear_command()`
  Remove the downlink command that was previously read. (link: [CMD_CR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#cmd_c-command-clear))
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `event_read()`
  Read the event register. (link: [EVT_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#evt_r-event-register-read))
  * Returns tuple (status, event_type):
    * `status`: (int) the status code of the operation
    * `event_type`: (int) enumeration code of event. Possible values are defined as macros at `astronode.EVENT_MSG_*`

  ### `read_satellite_ack()`
  Read Satellite ACK when a call to [ASTRONODEevent_read()](#event_read) returns `astronode.EVENT_MSG_ACK`. (link: [SAK_RR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#sak_r-read-satellite-ack))
  * Returns tuple (status, id):
    * `status`: (int) the status code of the operation
    * `id`: (2 bytes) the ID of the message

  ### `clear_satellite_ack()`
  Clear previously read Satellite ACK through `read_satellite_ack()`. (link: [SAK_CR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#sak_c-clear-satellite-ack))
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  ### `clear_reset_event()`: clear the Module Reset bit in the Event Register (link [RES_CR](https://docs.astrocast.com/docs/products/astronode-api/commands-definition#res_c-clear-reset-event))
  * Returns tuple (status, None):
    * `status`: (int) the status code of the operation

  

