"""Bénéfices industriels et commerciaux (BIC)."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Person as Individu


class bic_vente_fabrication_transformation_ca_ht(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "EA",
        1: "EB",
        2: "EC",
    }
    entity = Individu
    label = "Activités de ventes, fabrication, transformation : chiffre d’affaires hors taxes"
    definition_period = YEAR


class bic_vente_fabrication_transformation_achats(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "ED",
        1: "ED",
        2: "EF",
    }
    entity = Individu
    label = "Activités de ventes, fabrication, transformation : achats"
    definition_period = YEAR


class bic_vente_fabrication_transformation_salaires_et_sous_traitance(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "EG",
        1: "EH",
        2: "EI",
    }
    entity = Individu
    label = "Activités de ventes, fabrication, transformation : saalires nets versés et sous traitance"
    definition_period = YEAR


class bic_services_ca_ht(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "FA",
        1: "FB",
        2: "FC",
    }
    entity = Individu
    label = "Activités de ventes, fabrication, transformation : chiffre d’affaires hors taxes"
    definition_period = YEAR


class bic_services_achats(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "FD",
        1: "FD",
        2: "FF",
    }
    entity = Individu
    label = "Activités de ventes, fabrication, transformation : achats"
    definition_period = YEAR


class bic_services_salaires_et_sous_traitance(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = {
        0: "FG",
        1: "FH",
        2: "FI",
    }
    entity = Individu
    label = "Activités de ventes, fabrication, transformation : saalires nets versés et sous traitance"
    definition_period = YEAR


class bic_forfait(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Bénéfices indutriels et commerciaux au forfait"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        # Au forfait
        abattement = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.revenus_imposables.travailleurs_independants.bic.abattement
        return (
            max_(
                0,
                foyer_fiscal("bic_vente_fabrication_transformation_ca_ht", period)
                - foyer_fiscal("bic_vente_fabrication_transformation_achats", period)
                - foyer_fiscal(
                    "bic_vente_fabrication_transformation_salaires_et_sous_traitance",
                    period,
                )
                + foyer_fiscal("bic_services_ca_ht", period)
                - foyer_fiscal("bic_services_achats", period)
                - foyer_fiscal("bic_services_salaires_et_sous_traitance", period),
            )
            * abattement
        )
        # TODO: déduire reliquat de cotisations
