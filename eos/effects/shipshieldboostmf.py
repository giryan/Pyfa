# shipShieldBoostMF
#
# Used by:
# Ship: Breacher
type = "passive"
def handler(fit, ship, context):
    fit.modules.filteredItemBoost(lambda mod: mod.item.requiresSkill("Shield Operation"),
                                  "shieldBonus", ship.getModifiedItemAttr("shipBonusMF"), skill="Minmatar Frigate")
