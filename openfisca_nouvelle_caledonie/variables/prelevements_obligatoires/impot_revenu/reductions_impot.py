"""Réductions d'impots."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal


class reductions_impot(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Réduction d'impôt"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return (
            foyer_fiscal("reduction_impot_redistributive", period)
            )


class reduction_impot_redistributive(Variable):
    """Réduction d'impôt redistributive."""

    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Réduction d'impôt redistributive"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):

        parts_fiscales = foyer_fiscal("parts_fiscales", period)
        parts_fiscales_reduites = foyer_fiscal("parts_fiscales_reduites", period)
        parts_fiscales_redistributives = parts_fiscales - (parts_fiscales - parts_fiscales_reduites) / 2
        condtion = (
             foyer_fiscal("resident", period)
             & (foyer_fiscal("revenu_brut_global", period) <= 6100000 * parts_fiscales_redistributives)
            )
        redcution = (
            min_(
                max_(
                    0,
                    6100000 * parts_fiscales_redistributives - foyer_fiscal("revenu_brut_global", period),
                    ),
                20000 * parts_fiscales_redistributives,
                )
            )

        return condtion * redcution

        # )
		# // Condition pour bénéficier de cette RI :
		# // - RGB <= 6.100.000 * (N1 + (N2-N1)/2)
		# // - etre resident
		# // - reste_impot_brut <= 5.000
		# if (outs.getRevenuBrutGlobal() <= (6100000 * nb_parts_redistributive) && ins.isResident()) {
		# 	// calcul de la RI
		# 	if (outs.getRevenuBrutGlobal() >= 6080000 * nb_parts_redistributive) {
		# 		RI = (6100000 * nb_parts_redistributive) - outs.getRevenuBrutGlobal();
		# 	} else {
		# 		RI = min(1d / 100 * nb_parts_redistributive * outs.getRevenuBrutGlobal(), 20000 * nb_parts_redistributive);
		# 	}
		# }
