"""Bénéfices industriels et commerciaux (BIC)."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Individu


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
        1: "EE",
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
        1: "FE",
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

    def formula(individu, period, parameters):
        # Au forfait
        abattement = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.revenus_imposables.non_salarie.bic.abattement

        bic_vente = max_(
            (
                individu("bic_vente_fabrication_transformation_ca_ht", period)
                - individu("bic_vente_fabrication_transformation_achats", period)
                - individu(
                    "bic_vente_fabrication_transformation_salaires_et_sous_traitance",
                    period,
                )
            ),
            0,
        )
        bic_services = max_(
            (
                individu("bic_services_ca_ht", period)
                - individu("bic_services_achats", period)
                - individu("bic_services_salaires_et_sous_traitance", period)
            ),
            0,
        )
        return max_(
            0,
            (bic_vente + bic_services) * abattement
            - individu("cotisations_non_salarie", period),
        )


# Régime réel simplifié (Cadre 10 de la déclaration complémentaire)


class benefices_industriels_et_commerciaux_reel_simplifie(Variable):
    unit = "currency"
    cerfa_field = {
        0: "IA",
        1: "IB",
    }
    value_type = float
    entity = Individu
    label = "Bénéfices indutriels et commerciaux au régime réel simplifié"
    definition_period = YEAR


class deficits_industriels_et_commerciaux_reel_simplifie(Variable):
    unit = "currency"
    cerfa_field = {
        0: "ID",
        1: "IE",
    }
    value_type = float
    entity = Individu
    label = "Déficits indutriels et commerciaux au régime réel simplifié"
    definition_period = YEAR


# Régime réel normal (Cadre 10 de la déclaration complémentaire)


class benefices_industriels_et_commerciaux_reel_normal(Variable):
    unit = "currency"
    cerfa_field = {
        0: "LA",
        1: "LB",
    }
    value_type = float
    entity = Individu
    label = "Bénéfices indutriels et commerciaux au régime réel normal"
    definition_period = YEAR


class deficits_industriels_et_commerciaux_reel_normal(Variable):
    unit = "currency"
    cerfa_field = {
        0: "LJ",
        1: "LK",
    }
    value_type = float
    entity = Individu
    label = "Déficits indutriels et commerciaux au régime réel normal"
    definition_period = YEAR


class bic_reel(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Bénéfices indutriels et commerciaux au réel"
    definition_period = YEAR

    def formula(individu, period):
        # Au réel
        return max_(
            (
                individu("benefices_industriels_et_commerciaux_reel_simplifie", period)
                + individu("benefices_industriels_et_commerciaux_reel_normal", period)
                - individu("deficits_industriels_et_commerciaux_reel_simplifie", period)
                - individu("deficits_industriels_et_commerciaux_reel_normal", period)
            ),
            0,
        )


class bic(Variable):
    unit = "currency"
    value_type = float
    entity = Individu
    label = "Bénéfices indutriels et commerciaux"
    definition_period = YEAR

    def formula(individu, period):
        return individu("bic_reel", period) + individu("bic_forfait", period)
