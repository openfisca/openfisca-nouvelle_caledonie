"""Plus-values professionnelles."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Person as Individu


class plus_values_professionnelles_a_taux_reduit(Variable):
    unit = "currency"
    cerfa_field = {
        0: "LD",
        1: "LE",
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
    }
    value_type = float
    entity = Individu
    label = "Plus-values professionnelles imposées à taux normal"
    definition_period = YEAR
