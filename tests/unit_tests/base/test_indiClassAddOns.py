############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
from mw4.base.indiClassAddOns import INDI_TYPES, INDIGO_CONV


def test_indigo_conv_exists():
    assert INDIGO_CONV is not None


def test_indigo_conv_is_dict():
    assert isinstance(INDIGO_CONV, dict)


def test_indigo_conv_weather_barometer_mapping():
    key = "WEATHER_PARAMETERS.WEATHER_BAROMETER"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "WEATHER_PARAMETERS.WEATHER_PRESSURE"


def test_indigo_conv_sqm_device_mapping():
    assert "AUX_INFO.X_AUX_SKY_BRIGHTNESS" in INDIGO_CONV
    assert INDIGO_CONV["AUX_INFO.X_AUX_SKY_BRIGHTNESS"] == "SKY_QUALITY.SKY_BRIGHTNESS"


def test_indigo_conv_sqm_temperature_mapping():
    key = "AUX_INFO.X_AUX_SKY_TEMPERATURE"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "SKY_QUALITY.SKY_TEMPERATURE"


def test_indigo_conv_upb_device_average_mapping():
    key = "AUX_INFO.X_AUX_AVERAGE"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "POWER_CONSUMPTION.CONSUMPTION_AVG_AMPS"


def test_indigo_conv_upb_device_amphr_mapping():
    key = "AUX_INFO.X_AUX_AMP_HOUR"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "POWER_CONSUMPTION.CONSUMPTION_AMP_HOURS"


def test_indigo_conv_upb_device_watthr_mapping():
    key = "AUX_INFO.X_AUX_WATT_HOUR"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "POWER_CONSUMPTION.CONSUMPTION_WATT_HOURS"


def test_indigo_conv_upb_device_voltage_mapping():
    key = "AUX_INFO.X_AUX_VOLTAGE"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "POWER_SENSORS.SENSOR_VOLTAGE"


def test_indigo_conv_upb_device_current_mapping():
    key = "AUX_INFO.X_AUX_CURRENT"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "POWER_SENSORS.SENSOR_CURRENT"


def test_indigo_conv_upb_device_power_mapping():
    key = "AUX_INFO.X_AUX_POWER_OUTLET"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "POWER_SENSORS.SENSOR_POWER"


def test_indigo_conv_outlet_current_mappings():
    for i in range(1, 5):
        key = f"AUX_POWER_OUTLET_CURRENT.OUTLET_{i}"
        expected = f"POWER_CURRENT.POWER_CURRENT_{i}"
        assert key in INDIGO_CONV
        assert INDIGO_CONV[key] == expected


def test_indigo_conv_heater_outlet_current_mappings():
    outlet_map = {1: "A", 2: "B", 3: "C"}
    for i, letter in outlet_map.items():
        key = f"AUX_HEATER_OUTLET_CURRENT.OUTLET_{i}"
        expected = f"DEW_CURRENT.DEW_CURRENT_{letter}"
        assert key in INDIGO_CONV
        assert INDIGO_CONV[key] == expected


def test_indigo_conv_heater_outlet_mappings():
    outlet_map = {1: "A", 2: "B", 3: "C"}
    for i, letter in outlet_map.items():
        key = f"AUX_HEATER_OUTLET.OUTLET_{i}"
        expected = f"DEW_PWM.DEW_{letter}"
        assert key in INDIGO_CONV
        assert INDIGO_CONV[key] == expected


def test_indigo_conv_variable_power_outlet():
    key = "X_AUX_VARIABLE_POWER_OUTLET.OUTLET_1"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "ADJUSTABLE_VOLTAGE.ADJUSTABLE_VOLTAGE_VALUE"


def test_indigo_conv_power_outlet_switches():
    for i in range(1, 5):
        key = f"AUX_POWER_OUTLET.OUTLET_{i}"
        expected = f"POWER_CONTROL.POWER_CONTROL_{i}"
        assert key in INDIGO_CONV
        assert INDIGO_CONV[key] == expected


def test_indigo_conv_usb_port_switches():
    for i in range(1, 7):
        key = f"AUX_USB_PORT.PORT_{i}"
        expected = f"USB_PORT_CONTROL.PORT_{i}"
        assert key in INDIGO_CONV
        assert INDIGO_CONV[key] == expected


def test_indigo_conv_dew_control_manual():
    key = "AUX_DEW_CONTROL.MANUAL"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "AUTO_DEW.INDI_DISABLED"


def test_indigo_conv_dew_control_automatic():
    key = "AUX_DEW_CONTROL.AUTOMATIC"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "AUTO_DEW.INDI_ENABLED"


def test_indigo_conv_reboot():
    key = "X_AUX_REBOOT.REBOOT"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "REBOOT_DEVICE.REBOOT"


def test_indigo_conv_outlet_names():
    for i in range(1, 5):
        key = f"X_AUX_OUTLET_NAMES.POWER_OUTLET_NAME_{i}"
        expected = f"POWER_CONTROL_LABEL.POWER_LABEL_{i}"
        assert key in INDIGO_CONV
        assert INDIGO_CONV[key] == expected


def test_indigo_conv_uranus_meteo_pressure():
    key = "SENSORS.AbsolutePressure"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "WEATHER_PARAMETERS.WEATHER_PRESSURE"


def test_indigo_conv_uranus_meteo_dewpoint():
    key = "SENSORS.DewPoint"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "WEATHER_PARAMETERS.WEATHER_DEWPOINT"


def test_indigo_conv_uranus_meteo_temperature():
    key = "CLOUDS.CloudSkyTemperature"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "SKY_QUALITY.SKY_TEMPERATURE"


def test_indigo_conv_skyquality():
    key = "SKYQUALITY.MPAS"
    assert key in INDIGO_CONV
    assert INDIGO_CONV[key] == "SKY_QUALITY.SKY_BRIGHTNESS"


def test_indigo_conv_total_entries():
    expected_count = 41
    assert len(INDIGO_CONV) == expected_count


def test_indigo_conv_no_duplicate_keys():
    keys = list(INDIGO_CONV.keys())
    assert len(keys) == len(set(keys))


def test_indigo_conv_all_values_are_strings():
    for key, value in INDIGO_CONV.items():
        assert isinstance(key, str)
        assert isinstance(value, str)


def test_indigo_conv_values_not_empty():
    for key, value in INDIGO_CONV.items():
        assert len(key) > 0
        assert len(value) > 0


def test_indigo_conv_nonexistent_key():
    assert "NONEXISTENT.KEY" not in INDIGO_CONV


def test_indigo_conv_get_method():
    result = INDIGO_CONV.get("NONEXISTENT.KEY", "default")
    assert result == "default"


def test_indi_types_exists():
    assert INDI_TYPES is not None


def test_indi_types_is_dict():
    assert isinstance(INDI_TYPES, dict)


def test_indi_types_telescope():
    assert "telescope" in INDI_TYPES
    assert INDI_TYPES["telescope"] == (1 << 0)


def test_indi_types_camera():
    assert "camera" in INDI_TYPES
    assert INDI_TYPES["camera"] == (1 << 1)


def test_indi_types_guider():
    assert "guider" in INDI_TYPES
    assert INDI_TYPES["guider"] == (1 << 2)


def test_indi_types_focuser():
    assert "focuser" in INDI_TYPES
    assert INDI_TYPES["focuser"] == (1 << 3)


def test_indi_types_filterwheel():
    assert "filterwheel" in INDI_TYPES
    assert INDI_TYPES["filterwheel"] == (1 << 4)


def test_indi_types_dome():
    assert "dome" in INDI_TYPES
    assert INDI_TYPES["dome"] == (1 << 5)


def test_indi_types_observingconditions():
    assert "observingconditions" in INDI_TYPES
    expected = (1 << 7) | (1 << 15)
    assert INDI_TYPES["observingconditions"] == expected


def test_indi_types_skymeter():
    assert "skymeter" in INDI_TYPES
    expected = (1 << 15) | (1 << 19)
    assert INDI_TYPES["skymeter"] == expected


def test_indi_types_covercalibrator():
    assert "covercalibrator" in INDI_TYPES
    expected = (1 << 9) | (1 << 10)
    assert INDI_TYPES["covercalibrator"] == expected


def test_indi_types_switch():
    assert "switch" in INDI_TYPES
    expected = (1 << 7) | (1 << 3) | (1 << 15) | (1 << 18)
    assert INDI_TYPES["switch"] == expected


def test_indi_types_total_entries():
    expected_count = 10
    assert len(INDI_TYPES) == expected_count


def test_indi_types_no_duplicate_keys():
    keys = list(INDI_TYPES.keys())
    assert len(keys) == len(set(keys))


def test_indi_types_all_values_are_ints():
    for key, value in INDI_TYPES.items():
        assert isinstance(key, str)
        assert isinstance(value, int)


def test_indi_types_values_positive():
    for key, value in INDI_TYPES.items():
        assert value > 0


def test_indi_types_keys_are_strings():
    for key in INDI_TYPES:
        assert isinstance(key, str)
        assert len(key) > 0


def test_indi_types_nonexistent_key():
    assert "nonexistent" not in INDI_TYPES


def test_indi_types_get_method():
    result = INDI_TYPES.get("nonexistent", 0)
    assert result == 0


def test_indi_types_bit_values_correct():
    assert INDI_TYPES["telescope"] == 1
    assert INDI_TYPES["camera"] == 2
    assert INDI_TYPES["guider"] == 4
    assert INDI_TYPES["focuser"] == 8
    assert INDI_TYPES["filterwheel"] == 16
    assert INDI_TYPES["dome"] == 32


def test_indi_types_compound_values():
    assert INDI_TYPES["observingconditions"] == 128 + 32768
    assert INDI_TYPES["skymeter"] == 32768 + 524288
    assert INDI_TYPES["covercalibrator"] == 512 + 1024
    assert INDI_TYPES["switch"] == 128 + 8 + 32768 + 262144






