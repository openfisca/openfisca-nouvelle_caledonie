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
        return foyer_fiscal("reduction_impot_redistributive", period) - foyer_fiscal(
            "reduction_impots_reintegrees", period
        )


class reduction_impot_redistributive(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Réduction d'impôt redistributive"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        parts_fiscales = foyer_fiscal("parts_fiscales", period)
        parts_fiscales_reduites = foyer_fiscal("parts_fiscales_reduites", period)
        parts_fiscales_redistributives = (
            parts_fiscales - (parts_fiscales - parts_fiscales_reduites) / 2
        )
        resident = foyer_fiscal("resident", period)
        condtion = resident & (
            foyer_fiscal("revenu_brut_global", period)
            <= 6100000 * parts_fiscales_redistributives
        )
        revenu_brut_global = foyer_fiscal("revenu_brut_global", period)
        reduction = where(
            (revenu_brut_global <= 6_100_000 * parts_fiscales_redistributives)
            & resident,
            where(
                revenu_brut_global >= 6_080_000 * parts_fiscales_redistributives,
                6_100_000 * parts_fiscales_redistributives - revenu_brut_global,
                min(
                    0.01 * parts_fiscales_redistributives * revenu_brut_global,
                    20_000 * parts_fiscales_redistributives,
                ),
            ),
            0,
        )

        return condtion * reduction


class reduction_impots_reintegrees(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YN"
    label = "Réduction d'impôts des années précédentes réintégrées"
    definition_period = YEAR


class prestation_compensatoire(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YU"
    label = "Prestation compensatoire"
    definition_period = YEAR


class mecenat(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YY"
    label = "Mécénat"
    definition_period = YEAR


class cotisations_syndicales(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YJ"
    label = "Cotisations syndicales"
    definition_period = YEAR
