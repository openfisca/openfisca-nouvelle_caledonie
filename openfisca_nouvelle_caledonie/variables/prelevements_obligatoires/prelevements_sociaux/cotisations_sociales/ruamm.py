from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Person as Individu
from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.prelevements_sociaux.cotisations_sociales.helpers import (
    apply_bareme,
    apply_bareme_for_relevant_type_sal,
)
from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.prelevements_sociaux.cotisations_sociales.salarie import (
    TypesCategorieSalarie,
)


class ruamm_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation RUAMM employeur"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="employeur",
            bareme_name="ruamm",
            variable_name="ruamm_employeur",
        )
        return cotisation


class ruamm_salarie(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation RUAMM salarié"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="salarie",
            bareme_name="ruamm",
            variable_name="ruamm_salarie",
        )
        return cotisation
