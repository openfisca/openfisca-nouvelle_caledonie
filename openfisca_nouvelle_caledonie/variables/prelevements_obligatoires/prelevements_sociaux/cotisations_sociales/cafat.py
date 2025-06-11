from openfisca_core.model_api import *


from openfisca_nouvelle_caledonie.entities import Person as Individu
from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.prelevements_sociaux.cotisations_sociales.helpers import (
    apply_bareme,
    apply_bareme_for_relevant_type_sal,
    )

from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.prelevements_sociaux.cotisations_sociales.salarie import TypesCategorieSalarie


class accident_du_travail(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisations employeur accident du travail et maladie professionelle'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula_1991(individu, period, parameters):    # TODO : rajouter formule pré-1991 : s'applique au salaire sous PSS uniquement
        assiette = min_(
            individu('salaire_de_base', period),
            individu('plafond_cafat_autres_regimes', period)
        )
        taux_accident_du_travail = individu('taux_accident_du_travail', period)
        categorie_salarie = individu('categorie_salarie', period)
        assujetti = (
            (categorie_salarie == TypesCategorieSalarie.prive_non_cadre)
            + (categorie_salarie == TypesCategorieSalarie.prive_cadre)
            )
        # TODO: ajouter contractuel du public salarié de moins d'un an ou à temps partiel
        return assiette * taux_accident_du_travail * assujetti


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


class fds(Variable):
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
            variable_name = 'fds'
            )
        return cotisation


class fiaf(Variable):
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
            variable_name = 'fiaf'
            )
        return cotisation


class fsh(Variable):
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
            variable_name = 'fsh'
            )
        return cotisation


class prestations_familiales(Variable):
    value_type = float
    entity = Individu
    label = 'Cotisation prestations familiales (employeur seulement)'
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type = 'employeur',
            bareme_name = 'prestations_familiales',
            variable_name = 'prestations_familiales_employeur'
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
