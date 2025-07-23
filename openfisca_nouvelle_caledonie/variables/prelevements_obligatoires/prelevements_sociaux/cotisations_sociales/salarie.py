"""Cotisations sociales pour les salariés en Nouvelle-Calédonie."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Individu


class TypesCategorieSalarie(Enum):
    __order__ = "prive_non_cadre prive_cadre public_titulaire_etat public_titulaire_militaire public_titulaire_territoriale public_titulaire_hospitaliere public_non_titulaire non_pertinent"  # Needed to preserve the enum order in Python 2
    prive_non_cadre = "Non cadre du secteur privé"
    prive_cadre = "Cadre du secteur privé"
    public_titulaire_etat = "Titulaire de la fonction publique d'État"
    public_titulaire_militaire = "Titulaire de la fonction publique militaire"
    public_titulaire_territoriale = "Titulaire de la fonction publique territoriale"
    public_titulaire_hospitaliere = "Titulaire de la fonction publique hospitalière"
    public_non_titulaire = "Agent non-titulaire de la fonction publique"  # Les agents non titulaires, c’est-à-dire titulaires d’aucun grade de la fonction publique, peuvent être des contractuels, des vacataires, des auxiliaires, des emplois aidés…Les assistants maternels et familiaux sont eux aussi des non-titulaires.
    non_pertinent = "Non pertinent"


class TypesCotisationSocialeModeRecouvrement(Enum):
    __order__ = (
        "mensuel annuel mensuel_strict"  # Needed to preserve the enum order in Python 2
    )
    mensuel = "Mensuel avec régularisation en fin d'année"
    annuel = "Annuel"
    mensuel_strict = "Mensuel strict"


class categorie_salarie(Variable):
    value_type = Enum
    possible_values = TypesCategorieSalarie  # defined in model/base.py
    default_value = TypesCategorieSalarie.prive_non_cadre
    entity = Individu
    label = "Catégorie de salarié"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class cotisation_sociale_mode_recouvrement(Variable):
    value_type = Enum
    possible_values = TypesCotisationSocialeModeRecouvrement
    default_value = TypesCotisationSocialeModeRecouvrement.mensuel_strict
    entity = Individu
    label = "Mode de recouvrement des cotisations sociales"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class assiette_cotisations_sociales(Variable):
    value_type = float
    entity = Individu
    label = "Assiette des cotisations sociales des salaries"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    unit = "currency"

    def formula(individu, period):
        salaire_de_base = individu("salaire_de_base", period)
        categorie_salarie = individu("categorie_salarie", period)
        return (
            categorie_salarie != TypesCategorieSalarie.non_pertinent
        ) * salaire_de_base


class cotisations_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Cotisations sociales employeur"
    set_input = set_input_divide_by_period
    definition_period = MONTH
    calculate_output = calculate_output_add

    def formula(individu, period):
        # CAFAT
        accident_du_travail = individu("accident_du_travail", period)
        chomage = individu("chomage_employeur", period)
        fds = individu("fds", period)
        fiaf = individu("fiaf", period)
        fsh = individu("fsh", period)
        prestations_familiales = individu("prestations_familiales", period)
        retraite = individu("retraite_employeur", period)
        # RUAMM
        ruamm = individu("ruamm_employeur", period)
        # Retraite complémentaire
        agff_employeur = individu("agff_employeur", period)
        agirc_arrco_employeur = individu("agirc_arrco_employeur", period)
        agirc_employeur = individu("agirc_employeur", period)
        agirc_gmp_employeur = individu("agirc_gmp_employeur", period)
        arrco_employeur = individu("arrco_employeur", period)
        # chomage_employeur = individu('chomage_employeur', period)
        contribution_equilibre_general_employeur = individu(
            "contribution_equilibre_general_employeur", period
        )
        contribution_equilibre_technique_employeur = individu(
            "contribution_equilibre_technique_employeur", period
        )

        return (
            # CAFAT
            accident_du_travail
            + chomage
            + fds
            + fiaf
            + fsh
            + prestations_familiales
            + retraite
            # RUAMM
            + ruamm
            # Retraite complémentaire
            + agff_employeur
            + agirc_arrco_employeur
            + agirc_employeur
            + agirc_gmp_employeur
            + arrco_employeur
            + contribution_equilibre_general_employeur
            + contribution_equilibre_technique_employeur
        )


class cotisations_salariales(Variable):
    value_type = float
    entity = Individu
    label = "Cotisations sociales salariales"
    set_input = set_input_divide_by_period
    definition_period = MONTH
    calculate_output = calculate_output_add

    def formula(individu, period):
        # CAFAT
        retraite = individu("retraite_salarie", period, options=[ADD])
        chomage = individu("chomage_salarie", period, options=[ADD])
        # RUAMM
        ruamm = individu("ruamm_salarie", period, options=[ADD])
        # Retraite complémentaire
        agff_salarie = individu("agff_salarie", period)
        agirc_arrco_salarie = individu("agirc_arrco_salarie", period)
        agirc_salarie = individu("agirc_salarie", period)
        agirc_gmp_salarie = individu("agirc_gmp_salarie", period)
        arrco_salarie = individu("arrco_salarie", period)
        # chomage_salarie = individu('chomage_salarie', period)
        contribution_equilibre_general_salarie = individu(
            "contribution_equilibre_general_salarie", period
        )
        contribution_equilibre_technique_salarie = individu(
            "contribution_equilibre_technique_salarie", period
        )

        return (
            # CAFAT
            retraite
            + chomage
            # RUAMM
            + ruamm
            # Retraite complémentaire
            + agff_salarie
            + agirc_arrco_salarie
            + agirc_salarie
            + agirc_gmp_salarie
            + arrco_salarie
            + contribution_equilibre_general_salarie
            + contribution_equilibre_technique_salarie
        )


class salaire_net(Variable):
    value_type = float
    entity = Individu
    label = "Salaires nets"
    set_input = set_input_divide_by_period
    definition_period = MONTH

    def formula(individu, period):
        salaire_imposable = individu("salaire_de_base", period)
        cotisations_salariales = individu("cotisations_salariales", period)
        ccs = individu("ccs", period)

        return salaire_imposable - cotisations_salariales - ccs
