import pytest
from dataclasses import FrozenInstanceError
from mw4.logic.modelBuild.modelTypes import ModelRunConfig, ModelTiming
from pathlib import Path


def test_modelTiming_1():
    assert [int(t) for t in ModelTiming] == [0, 1, 2]
    assert ModelTiming.CONSERVATIVE == 0
    assert ModelTiming.PROGRESSIVE == 2


def test_modelRunConfig_1():
    config = ModelRunConfig()
    assert config.imageDir == Path()
    assert config.numberRetries == 0
    assert not config.retriesReverse
    assert config.waitTimeExposure == 0
    assert config.modelTiming == ModelTiming.CONSERVATIVE
    assert config.plateSolveApp == ""


def test_modelRunConfig_2():
    config = ModelRunConfig()
    with pytest.raises(FrozenInstanceError):
        config.numberRetries = 1
