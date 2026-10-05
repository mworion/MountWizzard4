from mw4.base.operationStatus import OperationStatus


def test_operationStatus_1():
    assert OperationStatus.IDLE == 0
    assert OperationStatus.MODEL_BATCH == 1
    assert OperationStatus.SOLVE == 7
    assert [int(s) for s in OperationStatus] == list(range(8))
