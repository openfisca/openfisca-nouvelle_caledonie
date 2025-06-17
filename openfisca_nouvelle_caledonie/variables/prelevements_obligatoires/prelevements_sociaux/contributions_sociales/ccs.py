from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Individu


class ccs(Variable):
    value_type = float
    entity = Individu
    label = "Contribution calédonienne de soliarité"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula_2015(individu, period, parameters):
        ccs = parameters(
            period
        ).prelevements_obligatoires.prelevements_sociaux.contribution_caledonienne_solidarite
        revenus_d_activite = individu("salaire_de_base", period)
        revenus_de_remplacement = (
            individu.empty_array()
        )  # TODO: Implement this variable
        revenus_epargne_patrimoine = (
            individu.empty_array()
        )  # TODO: Implement this variable
        contribution = (
            ccs.activite.calc(revenus_d_activite)
            + ccs.remplacement.calc(revenus_de_remplacement)
            + ccs.epargne_patrimoine.calc(revenus_epargne_patrimoine)
        )

        return contribution
