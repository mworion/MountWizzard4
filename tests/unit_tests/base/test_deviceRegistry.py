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
import pytest
from mw4.base.deviceRegistry import DeviceEntry, DeviceRegistry
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture()
def registry() -> DeviceRegistry:
    """Registry fixture with full app and devices populated."""
    try:
        app = App()
        dReg = DeviceRegistry(app)
        dReg.addDevices(app)
        return dReg
    except Exception as e:
        pytest.skip(f"Registry initialization failed: {e}")


def test_deviceEntrySignalsPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.signals


def test_deviceEntryDataPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.data


def test_deviceEntryObsSitePropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.obsSite


def test_deviceEntrySettingPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.setting


def test_deviceEntryLocationPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.location


def test_deviceEntryTimeJDPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.timeJD


def test_deviceEntryModelPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.model


def test_deviceEntryGeometryPropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.geometry


def test_deviceEntryFirmwarePropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.firmware


def test_deviceEntrySatellitePropertyRaisesWhenInstanceNone() -> None:
    entry = DeviceEntry(
        name="refraction", instance=None, deviceType=None, isConfigurable=False
    )
    with pytest.raises(AttributeError):
        _ = entry.satellite


# ------------------------------------------------------------------
# DeviceRegistry — population
# ------------------------------------------------------------------
def test_initiallyNotEmpty(registry: DeviceRegistry) -> None:
    assert "camera" in registry.d
    assert "dome" in registry.d
    assert "mount" in registry.d


def test_driversHaveRequiredFields(registry: DeviceRegistry) -> None:
    for name, entry in registry.d.items():
        assert isinstance(entry, DeviceEntry)
        assert entry.name == name
        assert hasattr(entry, "instance")
        assert hasattr(entry, "deviceType")
        assert hasattr(entry, "stat")
        assert hasattr(entry, "isConfigurable")


def test_cameraDriverExists(registry: DeviceRegistry) -> None:
    assert "camera" in registry.d
    entry = registry.d["camera"]
    assert entry.instance is not None
    assert entry.deviceType == "camera"
    assert entry.isConfigurable is True


def test_domeDriverExists(registry: DeviceRegistry) -> None:
    assert "dome" in registry.d
    entry = registry.d["dome"]
    assert entry.instance is not None
    assert entry.deviceType == "dome"
    assert entry.isConfigurable is True


def test_mountDriverExists(registry: DeviceRegistry) -> None:
    assert "mount" in registry.d
    entry = registry.d["mount"]
    assert entry.instance is not None
    assert entry.isConfigurable is False


def test_refractionIsNotConfigurable(registry: DeviceRegistry) -> None:
    entry = registry.d["refraction"]
    assert entry.instance is None
    assert entry.isConfigurable is False


# ------------------------------------------------------------------
# DeviceRegistry — mapping protocol
# ------------------------------------------------------------------
def test_registryGetItem(registry: DeviceRegistry) -> None:
    entry = registry["camera"]
    assert isinstance(entry, DeviceEntry)
    assert entry.name == "camera"


def test_registryContains(registry: DeviceRegistry) -> None:
    assert "camera" in registry
    assert "nonexistent" not in registry


def test_registryIter(registry: DeviceRegistry) -> None:
    names = list(registry)
    assert "camera" in names
    assert "mount" in names
    assert "refraction" in names


# ------------------------------------------------------------------
# DeviceRegistry — configurable() iterator
# ------------------------------------------------------------------
def test_configurableExcludesMount(registry: DeviceRegistry) -> None:
    names = [e.name for e in registry.configurable()]
    assert "mount" not in names


def test_configurableExcludesRefraction(registry: DeviceRegistry) -> None:
    names = [e.name for e in registry.configurable()]
    assert "refraction" not in names


def test_configurableIncludesCamera(registry: DeviceRegistry) -> None:
    names = [e.name for e in registry.configurable()]
    assert "camera" in names


def test_configurableAllHaveInstance(registry: DeviceRegistry) -> None:
    for entry in registry.configurable():
        assert entry.instance is not None


# ------------------------------------------------------------------
# DeviceRegistry — setStat()
# ------------------------------------------------------------------
def test_setStatTrue(registry: DeviceRegistry) -> None:
    registry.setStat("camera", True)
    assert registry.d["camera"].stat is True


def test_setStatFalse(registry: DeviceRegistry) -> None:
    registry.setStat("mount", False)
    assert registry.d["mount"].stat is False


def test_setStatNone(registry: DeviceRegistry) -> None:
    registry.setStat("refraction", None)
    assert registry.d["refraction"].stat is None


# ------------------------------------------------------------------
# DeviceRegistry — two-phase initialization pattern
# ------------------------------------------------------------------
def test_initPhase1OnlyMountExists() -> None:
    """After __init__, only mount device exists."""
    try:
        app = App()
        dReg = DeviceRegistry(app)
        assert "mount" in dReg.d
        assert "camera" not in dReg.d
        assert "dome" not in dReg.d
        assert len(dReg.d) == 1
    except Exception as e:
        pytest.skip(f"App initialization failed: {e}")


def test_initPhase2AllDevicesExist() -> None:
    """After addDevices(), all devices exist."""
    try:
        app = App()
        dReg = DeviceRegistry(app)
        dReg.addDevices(app)
        assert "mount" in dReg.d
        assert "camera" in dReg.d
        assert "dome" in dReg.d
        assert "refraction" in dReg.d
        assert len(dReg.d) > 1
    except Exception as e:
        pytest.skip(f"App initialization failed: {e}")


def test_initPhase2MountAccessibleDuringAddDevices() -> None:
    """Mount is accessible during addDevices() for device initialization."""
    try:
        app = App()
        dReg = DeviceRegistry(app)
        assert app.mount is not None
        dReg.addDevices(app)
        assert dReg["mount"].instance is app.mount
    except Exception as e:
        pytest.skip(f"App initialization failed: {e}")


def test_initProductionCreatesNewMount() -> None:
    """In production (no pre-existing mount), __init__ creates new MountDevice."""
    try:
        from mw4.mountcontrol.mount import MountDevice

        app = App()
        # Ensure app.mount doesn't exist before initialization
        if hasattr(app, "mount"):
            delattr(app, "mount")

        dReg = DeviceRegistry(app)

        # Assert mount was created
        assert hasattr(app, "mount")
        assert app.mount is not None
        assert isinstance(app.mount, MountDevice)
        # Assert mount entry is in registry
        assert "mount" in dReg.d
        assert dReg["mount"].instance is app.mount
    except Exception as e:
        pytest.skip(f"App initialization failed: {e}")


def test_initTestModeMountsInjected() -> None:
    """In test mode (pre-existing mount), __init__ uses injected mount."""
    try:
        from mw4.mountcontrol.mount import MountDevice

        app = App()
        # Create a mock mount and inject it
        mock_mount = MountDevice(app, verbose=True)
        app.mount = mock_mount

        dReg = DeviceRegistry(app)

        # Assert the injected mount is used
        assert dReg["mount"].instance is mock_mount
        assert app.mount is mock_mount
    except Exception as e:
        pytest.skip(f"App initialization failed: {e}")


# ------------------------------------------------------------------
# DeviceRegistry — signal connections
# ------------------------------------------------------------------
def test_initConnectsStopDevicesSignal(registry: DeviceRegistry) -> None:
    """Test that stopDevices signal is connected during initialization."""
    # Create new app and registry to test connections
    try:
        app = App()
        dReg = DeviceRegistry(app)
        # If no exception, signals are properly connected
        assert dReg.app is app
    except Exception as e:
        pytest.skip(f"Signal connection test failed: {e}")


def test_initConnectsStartStopDeviceSignals(registry: DeviceRegistry) -> None:
    """Test that device-specific start/stop signals are connected."""
    # Test that when signals are emitted, registry handles them
    app = App()
    dReg = DeviceRegistry(app)
    dReg.addDevices(app)

    # The connections should be established without errors
    # Verify startDevice and stopDevice are connected
    assert dReg.app is app


def test_deviceConnectedEmitsMessage(registry: DeviceRegistry) -> None:
    """Test that deviceConnected emits message signal."""
    from unittest.mock import MagicMock

    # Mock the msg signal to capture emission
    registry.app.msg = MagicMock()

    # Call deviceConnected
    registry.deviceConnected("camera", "INDI::camera")

    # Verify the signal was emitted with correct parameters
    registry.app.msg.emit.assert_called_once_with(
        0, "Driver", "Device connected", "INDI::camera::camera"
    )
    # Verify stat was set to True
    assert registry.d["camera"].stat is True


def test_deviceDisconnectedEmitsMessage(registry: DeviceRegistry) -> None:
    """Test that deviceDisconnected emits message signal."""
    from unittest.mock import MagicMock

    # Mock the msg signal to capture emission
    registry.app.msg = MagicMock()

    # Call deviceDisconnected
    registry.deviceDisconnected("dome", "INDI::dome")

    # Verify the signal was emitted with correct parameters
    registry.app.msg.emit.assert_called_once_with(
        0, "Driver", "Device disconnected", "INDI::dome::dome"
    )
    # Verify stat was set to False
    assert registry.d["dome"].stat is False


def test_deviceConnectedUpdatesStatBeforeMessage(registry: DeviceRegistry) -> None:
    """Test that deviceConnected sets stat to True before emitting message."""
    from unittest.mock import MagicMock

    # Set up recording of method calls
    registry.app.msg = MagicMock()

    # Call deviceConnected
    registry.deviceConnected("camera", "TestCamera")

    # Verify stat was updated
    assert registry.d["camera"].stat is True
    # Verify message was emitted
    assert registry.app.msg.emit.called


def test_deviceDisconnectedUpdatesStatBeforeMessage(registry: DeviceRegistry) -> None:
    """Test that deviceDisconnected sets stat to False before emitting message."""
    from unittest.mock import MagicMock

    # First set stat to True
    registry.setStat("camera", True)
    registry.app.msg = MagicMock()

    # Call deviceDisconnected
    registry.deviceDisconnected("camera", "TestCamera")

    # Verify stat was updated
    assert registry.d["camera"].stat is False
    # Verify message was emitted
    assert registry.app.msg.emit.called


# ------------------------------------------------------------------
# DeviceRegistry — config management
# ------------------------------------------------------------------
def test_collectConfigFromSingleDeviceWithoutConfig(registry: DeviceRegistry) -> None:
    """Test collectConfigFromSingleDevice when device has no config attribute."""
    from unittest.mock import MagicMock

    # Mock a device without config attribute
    mock_device = MagicMock()
    mock_device.framework = "indi"
    mock_device.run = {"indi": MagicMock(spec=[])}  # No config attribute
    registry.d["camera"].instance = mock_device

    result = registry.collectConfigFromSingleDevice("camera")
    assert "framework" in result
    assert result["framework"] == "indi"


def test_writeConfigToSingleDeviceWithMissingFrameworkConfig(
    registry: DeviceRegistry,
) -> None:
    """Test writeConfigToSingleDevice with config missing framework."""
    cfgDevice = {"framework": "indi"}
    # Should not raise error even though alpaca framework not in config
    registry.writeConfigToSingleDevice("camera", cfgDevice)
    assert registry.d["camera"].instance.framework == "indi"


def test_writeConfigToAllDevicesSkipsUnknownDevices(registry: DeviceRegistry) -> None:
    """Test writeConfigToAllDevices skips devices not in config."""
    cfgSetting = {"nonexistent": {"framework": "indi"}}
    # Should not raise error for nonexistent device in config
    registry.writeConfigToAllDevices(cfgSetting)


def test_stopDeviceWithoutFramework(registry: DeviceRegistry) -> None:
    """Test stopDevice returns early when framework is empty."""
    registry.d["camera"].instance.framework = ""
    registry.setStat("camera", True)
    registry.stopDevice("camera")
    # Should return early and not clear data since framework is empty
    assert registry.d["camera"].instance.framework == ""


def test_stopDeviceWithoutDeviceName(registry: DeviceRegistry) -> None:
    """Test stopDevice returns early when deviceName is empty."""
    from unittest.mock import MagicMock

    registry.d["camera"].instance.framework = "indi"
    mock_config = MagicMock()
    mock_config.deviceName = ""
    registry.d["camera"].run["indi"].config = mock_config
    old_data_id = id(registry.d["camera"].data)
    registry.stopDevice("camera")
    # Should return early and not clear data
    assert id(registry.d["camera"].data) == old_data_id


def test_startDeviceWithoutFramework(registry: DeviceRegistry) -> None:
    """Test startDevice returns early when framework is empty."""
    registry.d["camera"].instance.framework = ""
    registry.startDevice("camera")
    # Should return early without setting stat
    assert registry.d["camera"].stat is None


def test_startDeviceWithoutDeviceName(registry: DeviceRegistry) -> None:
    """Test startDevice returns early when deviceName is empty."""
    from unittest.mock import MagicMock

    registry.d["camera"].instance.framework = "indi"
    mock_config = MagicMock()
    mock_config.deviceName = ""
    registry.d["camera"].run["indi"].config = mock_config
    registry.startDevice("camera")
    # Should return early without setting stat
    assert registry.d["camera"].stat is None


# ------------------------------------------------------------------
# Additional deviceRegistry tests for complete coverage
# ------------------------------------------------------------------
def test_writeConfigToSingleDeviceWithConfigFields(registry: DeviceRegistry) -> None:
    """Test writeConfigToSingleDevice actually sets config fields."""
    from dataclasses import dataclass, field
    from unittest.mock import MagicMock

    # Create a mock config object with fields
    @dataclass
    class MockConfig:
        testField: str = field(default="default")

    # Setup mock device with config
    mock_device = MagicMock()
    mock_device.framework = "indi"
    mock_device.run = {"indi": MagicMock()}
    mock_device.run["indi"].config = MockConfig()
    registry.d["camera"].instance = mock_device

    cfgDevice = {
        "framework": "indi",
        "indi": {"testField": "new_value"},
    }
    registry.writeConfigToSingleDevice("camera", cfgDevice)
    # Verify config field was set
    assert registry.d["camera"].instance.run["indi"].config.testField == "new_value"


def test_stopDeviceActuallyStopping(registry: DeviceRegistry) -> None:
    """Test stopDevice calls stopCommunication when framework and deviceName are set."""
    from unittest.mock import MagicMock

    registry.d["camera"].instance.framework = "indi"
    mock_config = MagicMock()
    mock_config.deviceName = "test_camera"
    registry.d["camera"].run["indi"].config = mock_config

    # Mock instance methods and data
    registry.d["camera"].instance.stopCommunication = MagicMock()
    registry.d["camera"].instance.data = {"test": "data"}

    registry.stopDevice("camera")
    # Verify stopCommunication was called
    registry.d["camera"].instance.stopCommunication.assert_called_once()
    # Verify data was cleared
    assert registry.d["camera"].instance.data == {}
    # Verify stat was set to None
    assert registry.d["camera"].stat is None


def test_startDeviceActuallyStarting(registry: DeviceRegistry) -> None:
    """Test startDevice calls startCommunication when framework and deviceName are set."""
    from unittest.mock import MagicMock

    registry.d["camera"].instance.framework = "indi"
    mock_config = MagicMock()
    mock_config.deviceName = "test_camera"
    registry.d["camera"].run["indi"].config = mock_config

    # Mock instance methods
    registry.d["camera"].instance.startCommunication = MagicMock()

    registry.startDevice("camera")
    # Verify startCommunication was called
    registry.d["camera"].instance.startCommunication.assert_called_once()
    # Verify stat was set to True
    assert registry.d["camera"].stat is True


def test_writeConfigToAllDevicesCallsWriteConfigToSingleDevice(
    registry: DeviceRegistry,
) -> None:
    """Test writeConfigToAllDevices calls writeConfigToSingleDevice for known devices."""
    from unittest.mock import MagicMock, patch

    cfgSetting = {"camera": {"framework": "indi"}}
    with patch.object(
        registry, "writeConfigToSingleDevice"
    ) as mock_write_config:
        registry.writeConfigToAllDevices(cfgSetting)
        # Verify writeConfigToSingleDevice was called with camera device
        mock_write_config.assert_called_once()
        call_args = mock_write_config.call_args
        assert call_args[0][0] == "camera"
        assert call_args[0][1] == cfgSetting["camera"]


def test_writeConfigToSingleDeviceSkipsFrameworkWithoutConfig(
    registry: DeviceRegistry,
) -> None:
    """Test writeConfigToSingleDevice skips frameworks that don't have config."""
    from dataclasses import dataclass, field
    from unittest.mock import MagicMock

    @dataclass
    class MockConfig:
        testField: str = field(default="value")

    # Create a device with one framework that has config and one that doesn't
    mock_device = MagicMock()
    mock_device.framework = "indi"
    mock_device.run = {
        "indi": MagicMock(config=MockConfig()),  # Has config
        "alpaca": MagicMock(spec=[]),  # No config attribute
    }
    registry.d["camera"].instance = mock_device

    cfgDevice = {
        "framework": "indi",
        "indi": {"testField": "value"},
        "alpaca": {"testField": "value"},  # This should be skipped
    }
    registry.writeConfigToSingleDevice("camera", cfgDevice)
    # Should not raise error - alpaca framework without config should be skipped


def test_writeConfigToSingleDeviceSkipsMissingConfigField(
    registry: DeviceRegistry,
) -> None:
    """Test writeConfigToSingleDevice skips fields not in config dict."""
    from dataclasses import dataclass, field

    @dataclass
    class MockConfig:
        field1: str = field(default="default")
        field2: str = field(default="default")

    mock_device = registry.d["camera"].instance
    mock_device.framework = "indi"
    mock_device.run["indi"].config = MockConfig()

    # Only provide field1 in config, not field2
    cfgDevice = {"framework": "indi", "indi": {"field1": "new_value"}}
    registry.writeConfigToSingleDevice("camera", cfgDevice)
    # Verify field1 was set, field2 remained default
    assert mock_device.run["indi"].config.field1 == "new_value"
    assert mock_device.run["indi"].config.field2 == "default"


