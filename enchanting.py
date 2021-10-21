#!/usr/bin/env python3
from enum import Enum
from typing import Dict, Tuple, List
import argparse
import math
import random


class EnchantmentType(Enum):
    FINITE_CHARGES = "FINITE_CHARGES"
    DAILY_CHARGES = "DAILY_CHARGES"
    COOLDOWN = "COOLDOWN"
    CONSTANT = "CONSTANT"


class TimeFactor(Enum):
    RUSHING = 0.5
    RUSHING_EVEN_MORE = 0.25
    NORMAL = 0.0
    PAITENCE = 2.0
    EVEN_MORE_PAITENCE = 4.0


enchantment_types_to_skilldays: Dict[EnchantmentType, Tuple[int, bool]] = {
    EnchantmentType.FINITE_CHARGES: (50, False),
    EnchantmentType.DAILY_CHARGES: (125, True),
    EnchantmentType.COOLDOWN: (500, True),
    EnchantmentType.CONSTANT: (5000, True)
}


def ease_of_enchantment(skill: int, quality: int, spell_level: int, unfamiliarity: int) -> int:
    return skill + quality - spell_level - unfamiliarity


def num_charges(ease_of_enchantment: int) -> int:
    return max(1, math.floor(float(ease_of_enchantment) / 2))


def enchantment_time(ease: int, skill_days: int) -> int:
    return math.floor(skill_days / math.pow(ease, 2))


def _volatility_from_time(time_factor: TimeFactor) -> int:
    if time_factor is TimeFactor.NORMAL:
        return 0
    return -1 * int(math.log2(time_factor.value))


def _volatility_from_spell_level(spell_level: int) -> int:
    return min(int(float(spell_level) / 3), 3)  # 3-5 -> 1, 6-8 -> 2, 9 -> 3


def _volatility_from_ease(ease: int) -> int:
    if 1 <= ease < 5:
        return 0
    elif ease >= 5 and ease <= 9:
        return -1
    elif ease >= 10 and ease <= 14:
        return -2
    elif ease >= 15:
        return -3
    else:
        raise ValueError


def calculate_volatility(enchantment_type: EnchantmentType,
                         spell_level: int,
                         time_factor: TimeFactor,
                         enchantment_ease: int,
                         existing_enchantments: int) -> int:

    ENCHANTMENT_TYPE_TO_VOLATILITY: Dict[EnchantmentType, int] = {
        EnchantmentType.DAILY_CHARGES: 2,
        EnchantmentType.COOLDOWN: 3,
        EnchantmentType.CONSTANT: 4
    }

    vol_from_spell_level = _volatility_from_spell_level(spell_level)
    vol_from_time = _volatility_from_time(time_factor)
    vol_from_ease = _volatility_from_ease(enchantment_ease)

    if existing_enchantments > 0:
        vol_from_existing: int = pow(2, existing_enchantments)
    else:
        vol_from_existing = 0

    volatility = sum([ENCHANTMENT_TYPE_TO_VOLATILITY[enchantment_type],
                     vol_from_spell_level,
                     vol_from_time,
                     vol_from_existing,
                     vol_from_ease])
    return volatility


POSSIBLE_COSTS_OF_USE = {
    1: ["2d4_DAMAGE", "WASTE", "FIZZLE", "UNTAMED_MAGIC"],
    2: ["3d6_DAMAGE", "FERAL_MAGIC", "BACKFIRE", "DESTRUCTION"],
    3: ["DESTRUCTION"]
}


def cost_of_use(volatility_level) -> List[str]:
    costs: List[str] = []
    while volatility_level > 0:
        if volatility_level >= 3:
            costs += POSSIBLE_COSTS_OF_USE[3]
            volatility_level -= 3
            continue
        else:
            possible_costs = POSSIBLE_COSTS_OF_USE[volatility_level]
            costs.append(possible_costs[random.randint(0, len(possible_costs) - 1)])
            volatility_level -= volatility_level

    return costs


class Enchantment():
    def __init__(self):
        self.etype: EnchantmentType = EnchantmentType.FINITE_CHARGES
        self.ease: int = 0
        self.time_to_enchant: int = 0
        self.cost: List[str] = list()
        self.charges: int = -1
        self.volatility: int = 0

    def print_enchantment(self):
        output = ""
        output += f"Will take {self.time_to_enchant} days."
        if self.charges > 0:
            output += f" Has {self.charges} charges."
        if len(self.cost) > 0:
            output += f" Costs of use are: {self.cost}"
        print(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--caster-level", required=True, type=int)
    parser.add_argument("--spell-level", required=True, type=int)
    parser.add_argument("--vessel-level", required=True, type=int)
    parser.add_argument("--unfamiliarity", required=True, type=int)
    parser.add_argument("--enchant-type", required=True, type=str)
    parser.add_argument("--time-factor", required=True, type=str)
    parser.add_argument("--existing-enchantments", required=True, type=int, default=0)
    args = parser.parse_args()

    enchantment = Enchantment()

    enchantment.ease = ease_of_enchantment(
        args.caster_level,
        args.vessel_level,
        args.spell_level,
        args.unfamiliarity
    )

    if EnchantmentType[args.enchant_type] == EnchantmentType.DAILY_CHARGES:
        enchantment.charges = num_charges(enchantment.ease)

    enchantment.etype = EnchantmentType[args.enchant_type]

    enchantment.volatility = calculate_volatility(
        enchantment.etype,
        args.spell_level,
        TimeFactor[args.time_factor],
        enchantment.ease,
        args.existing_enchantments
    )

    skill_days_required = enchantment_types_to_skilldays[enchantment.etype][0]
    enchantment.time_to_enchant = enchantment_time(enchantment.ease, skill_days_required)
    enchantment.cost = cost_of_use(enchantment.volatility)

    enchantment.print_enchantment()


if __name__ == "__main__":
    main()
