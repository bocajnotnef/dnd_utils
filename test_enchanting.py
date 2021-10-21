import enchanting


def test_volatility_from_strength():
    assert(enchanting._volatility_from_spell_level(3) == 1)
    assert(enchanting._volatility_from_spell_level(5) == 1)
    assert(enchanting._volatility_from_spell_level(6) == 2)
    assert(enchanting._volatility_from_spell_level(9) == 3)


def test_volatility_from_time():
    assert(enchanting._volatility_from_time(enchanting.TimeFactor.RUSHING) == 1)
    assert(enchanting._volatility_from_time(enchanting.TimeFactor.RUSHING_EVEN_MORE) == 2)
    assert(enchanting._volatility_from_time(enchanting.TimeFactor.PAITENCE) == -1)
    assert(enchanting._volatility_from_time(enchanting.TimeFactor.EVEN_MORE_PAITENCE) == -2)
    assert(enchanting._volatility_from_time(enchanting.TimeFactor.NORMAL) == 0)


def test_volatility():
    first = enchanting.calculate_volatility(enchanting.EnchantmentType.DAILY_CHARGES,
                                            1,
                                            enchanting.TimeFactor.RUSHING_EVEN_MORE, 1, 0)
    assert(first == 4)

    second = enchanting.calculate_volatility(enchanting.EnchantmentType.DAILY_CHARGES,
                                             2,
                                             enchanting.TimeFactor.RUSHING_EVEN_MORE, 5, 0)