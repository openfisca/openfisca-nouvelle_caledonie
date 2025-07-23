"""Revenus d'activité."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Individu


class salaire_de_base(Variable):
    value_type = float
    entity = Individu
    label = "Salaire de base"
    set_input = set_input_divide_by_period
    definition_period = MONTH
    unit = "currency"
