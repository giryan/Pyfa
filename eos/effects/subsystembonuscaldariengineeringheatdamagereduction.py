# subsystemBonusCaldariEngineeringHeatDamageReduction
#
# Used by:
# Subsystem: Tengu Engineering - Supplemental Coolant Injector
type = "passive"
def handler(fit, module, context):
    fit.modules.filteredItemBoost(lambda mod: True, "heatDamage",
                                  module.getModifiedItemAttr("subsystemBonusCaldariEngineering"), skill="Caldari Engineering Systems")
