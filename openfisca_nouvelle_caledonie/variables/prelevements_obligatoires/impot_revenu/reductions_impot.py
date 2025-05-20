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
        return foyer_fiscal("reduction_impot_redistributive", period)


class reduction_impot_redistributive(Variable):
    """Réduction d'impôt redistributive."""

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
        condtion = foyer_fiscal("resident", period) & (
            foyer_fiscal("revenu_brut_global", period)
            <= 6100000 * parts_fiscales_redistributives
        )
        redcution = min_(
            max_(
                0,
                6100000 * parts_fiscales_redistributives
                - foyer_fiscal("revenu_brut_global", period),
            ),
            20000 * parts_fiscales_redistributives,
        )

        return condtion * redcution


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
