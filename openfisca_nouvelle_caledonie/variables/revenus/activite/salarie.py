"""Revenus d'activité."""

from openfisca_core.model_api import *

from openfisca_nouvelle_caledonie.entities import Individu

class TypesCategorieSalarie(Enum):
    __order__ = 'prive_non_cadre prive_cadre public_titulaire_etat public_titulaire_militaire public_titulaire_territoriale public_titulaire_hospitaliere public_non_titulaire non_pertinent'  # Needed to preserve the enum order in Python 2
    prive_non_cadre = 'Non cadre du secteur privé'
    prive_cadre = 'Cadre du secteur privé'
    public_titulaire_etat = "Titulaire de la fonction publique d'État"
    public_titulaire_militaire = 'Titulaire de la fonction publique militaire'
    public_titulaire_territoriale = 'Titulaire de la fonction publique territoriale'
    public_titulaire_hospitaliere = 'Titulaire de la fonction publique hospitalière'
    public_non_titulaire = 'Agent non-titulaire de la fonction publique'  # Les agents non titulaires, c’est-à-dire titulaires d’aucun grade de la fonction publique, peuvent être des contractuels, des vacataires, des auxiliaires, des emplois aidés…Les assistants maternels et familiaux sont eux aussi des non-titulaires.
    non_pertinent = 'Non pertinent'


class TypesCotisationSocialeModeRecouvrement(Enum):
    __order__ = 'mensuel annuel mensuel_strict'  # Needed to preserve the enum order in Python 2
    mensuel = "Mensuel avec régularisation en fin d'année"
    annuel = 'Annuel'
    mensuel_strict = 'Mensuel strict'


class categorie_salarie(Variable):
    value_type = Enum
    possible_values = TypesCategorieSalarie  # defined in model/base.py
    default_value = TypesCategorieSalarie.prive_non_cadre
    entity = Individu
    label = 'Catégorie de salarié'
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class cotisation_sociale_mode_recouvrement(Variable):
    value_type = Enum
    possible_values = TypesCotisationSocialeModeRecouvrement
    default_value = TypesCotisationSocialeModeRecouvrement.mensuel_strict
    entity = Individu
    label = 'Mode de recouvrement des cotisations sociales'
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class salaire_de_base(Variable):
    value_type = float
    entity = Individu
    label = 'Salaire de base'
    set_input = set_input_divide_by_period
    definition_period = MONTH
    unit = 'currency'
