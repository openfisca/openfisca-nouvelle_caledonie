from openfisca_core.model_api import *


from openfisca_nouvelle_caledonie.entities import Person as Individu
from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.prelevements_sociaux.cotisations_sociales.helpers import (
    apply_bareme,
    apply_bareme_for_relevant_type_sal,
    )

from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.prelevements_sociaux.cotisations_sociales.salarie import TypesCategorieSalarie


class chomage_employeur(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation chômage employeur'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'employeur',
            bareme_name = 'chomage',
            variable_name = 'chomage_employeur'
            )
        return cotisation


class chomage_salarie(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation chômage salarié'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'salarie',
            bareme_name = 'chomage',
            variable_name = 'chomage_salarie'
            )
        return cotisation


class fds_employeur(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation FDS employeur'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'employeur',
            bareme_name = 'fds',
            variable_name = 'fds_employeur'
            )
        return cotisation


class fiaf_salarie(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation FIAF salarié'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'salarie',
            bareme_name = 'fiaf',
            variable_name = 'fiaf_salarie'
            )
        return cotisation


class fiaf_employeur(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation FIAF employeur'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'employeur',
            bareme_name = 'fiaf',
            variable_name = 'fiaf_employeur'
            )
        return cotisation


class fiaf_salarie(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation FIAF salarié'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'salarie',
            bareme_name = 'fiaf',
            variable_name = 'fiaf_salarie'
            )
        return cotisation


class fsh_employeur(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation FSH employeur'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'employeur',
            bareme_name = 'fsh',
            variable_name = 'fsh_employeur'
            )
        return cotisation


class fsh_salarie(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation FSH salarié'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'salarie',
            bareme_name = 'fsh',
            variable_name = 'chomage_salarie'
            )
        return cotisation


class retraite_employeur(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation retraite employeur'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'employeur',
            bareme_name = 'retraite',
            variable_name = 'retraite_employeur'
            )
        return cotisation


class retraite_salarie(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation retraite salarié'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'salarie',
            bareme_name = 'retraite',
            variable_name = 'retraite_salarie'
            )
        return cotisation
