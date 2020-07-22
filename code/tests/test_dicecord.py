from dicecord import DicecordBot


def test_get_pool():
    # arrange
    text = 'roll pool 2 + 3'
    roller = DicecordBot(None, None, None)
    expected = 5
    # actual
    actual, _ = roller.get_pool(text)
    # assert
    assert expected == actual


def test_get_pool_with_8again():
    # arrange
    text = 'roll pool 2 + 3 8again'
    roller = DicecordBot(None, None, None)
    expected = 5
    # actual
    actual, _ = roller.get_pool(text)
    # assert
    assert expected == actual
