"""Traitements, alaires, pensions et rentes."""

from openfisca_core.periods import Period

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal, Person as Individu


class revenus_categoriels_tspr(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Revenus catégoriels des traitements, salaires, pensions et rentes"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        salaire_imposable_apres_deduction_et_abattement = foyer_fiscal('salaire_imposable_apres_deduction_et_abattement', period)
        pension_imposable_apres_deduction_et_abattement = foyer_fiscal('pension_imposable_apres_deduction_et_abattement', period)

        return salaire_imposable_apres_deduction_et_abattement + pension_imposable_apres_deduction_et_abattement
