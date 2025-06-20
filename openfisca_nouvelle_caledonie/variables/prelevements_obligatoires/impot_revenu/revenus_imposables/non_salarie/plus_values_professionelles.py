"""Plus-values professionnelles."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal, Individu


class plus_values_professionnelles_a_taux_reduit(Variable):
    unit = "currency"
    cerfa_field = {
        0: "LD",
        1: "LE",
        2: "LF",
    }
    value_type = float
    entity = Individu
    label = "Plus-values professionnelles imposées à taux réduit"
    definition_period = YEAR


class plus_values_professionnelles_a_taux_normal(Variable):
    unit = "currency"
    cerfa_field = {
        0: "LG",
        1: "LH",
        2: "LI",
    }
    value_type = float
    entity = Individu
    label = "Plus-values professionnelles imposées à taux normal"
    definition_period = YEAR


class plus_values_professionnelles(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Plus-values professionnelles"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        plus_values = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.revenus_imposables.non_salarie.plus_values
        return foyer_fiscal.sum(
            foyer_fiscal.members("plus_values_professionnelles_a_taux_reduit", period)
            * plus_values.taux_reduit
            + foyer_fiscal.members("plus_values_professionnelles_a_taux_normal", period)
            * plus_values.taux_normal
        )
