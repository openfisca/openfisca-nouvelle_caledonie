"""Réductions d'impots."""

from openfisca_core.model_api import *
from numpy import ceil
from openfisca_nouvelle_caledonie.entities import FoyerFiscal


class reductions_impot(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Réduction d'impôt"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return (
            foyer_fiscal("reduction_impot_redistributive", period)
            + foyer_fiscal("reduction_mecenat", period)
            + foyer_fiscal("reduction_cotisations_syndicales", period)
            + foyer_fiscal("reduction_prestation_compensatoire", period)
            + foyer_fiscal("reduction_investissement_locatif", period)
            + foyer_fiscal("reduction_dons_courses_hippiques", period)
            + foyer_fiscal("reduction_versements_promotion_exportation", period)
            + foyer_fiscal("reduction_souscription_via_plateforme_de_financement_participatif", period)
            + foyer_fiscal("reduction_dons_organismes_aide_pme", period)
            - foyer_fiscal("reduction_impots_reintegrees", period)
        )


class reduction_impot_redistributive(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    label = "Réduction d'impôt redistributive"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        parts_fiscales = foyer_fiscal("parts_fiscales", period)
        parts_fiscales_reduites = foyer_fiscal("parts_fiscales_reduites", period)
        parts_fiscales_redistributives = (
            parts_fiscales - (parts_fiscales - parts_fiscales_reduites) / 2
        )
        resident = foyer_fiscal("resident", period)
        condtion = resident & (
            foyer_fiscal("revenu_brut_global", period)
            <= 6100000 * parts_fiscales_redistributives   # TODO: parameters
        )
        revenu_brut_global = foyer_fiscal("revenu_brut_global", period)
        reduction = where(
            (revenu_brut_global <= 6_100_000 * parts_fiscales_redistributives)
            & resident,
            where(
                revenu_brut_global >= 6_080_000 * parts_fiscales_redistributives,
                6_100_000 * parts_fiscales_redistributives - revenu_brut_global,
                min_(
                    0.01 * parts_fiscales_redistributives * revenu_brut_global,
                    20_000 * parts_fiscales_redistributives,
                ),
            ),
            0,
        )
        return round_(condtion * reduction)


class reduction_impots_reintegrees(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YN"
    label = "Réduction d'impôts des années précédentes réintégrées"
    definition_period = YEAR


class prestation_compensatoire(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YU"
    label = "Prestation compensatoire"
    definition_period = YEAR


class reduction_prestation_compensatoire(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    label = "Réduction d'impôt pour prestation compensatoire"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        resident = foyer_fiscal("resident", period)
        reduction = min_(ceil(foyer_fiscal("prestation_compensatoire", period) * .25), 1_000_000)  # TODO: parameters
        return where(
            resident,
            reduction,
            0)


class mecenat(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    cerfa_field = "YY"
    label = "Mécénat"
    definition_period = YEAR


class reduction_mecenat(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    label = "Réduction d'impôt pour mécénat"
    definition_period = YEAR

    def formula_2024(foyer_fiscal, period):
        plafond = ceil(foyer_fiscal("revenu_net_global_imposable", period) * .15)  # TODO: parameters
        reduction = ceil(min_(foyer_fiscal("mecenat", period), plafond) * .75)  # TODO: parameters
        resident = foyer_fiscal("resident", period)
        return where(
            resident,
            reduction,
            0
        )

    def formula_2023(foyer_fiscal, period):
        plafond = ceil(foyer_fiscal("revenu_net_global_imposable", period) * .15)  # TODO: parameters et retirer lles formules inutilies
        reduction = ceil(min_(foyer_fiscal("mecenat", period), plafond) * .8)  # TODO: parameters
        resident = foyer_fiscal("resident", period)
        return where(
            resident,
            reduction,
            0
        )


class cotisations_syndicales(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    cerfa_field = "YJ"
    label = "Cotisations syndicales"
    definition_period = YEAR


class reduction_cotisations_syndicales(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    label = "Réduction d'impôt pour cotisations syndicales"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        plafond = ceil(foyer_fiscal("revenus_bruts_salaires_pensions", period) * .01)
        return ceil(
            min_(
                foyer_fiscal("cotisations_syndicales", period),
                plafond
            ) * 0.66
        )  # TODO: parameters


class dons_courses_hippiques(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    cerfa_field = "YL"
    label = "Dons au profit des comités d'organisation des courses hippiques"
    definition_period = YEAR


class reduction_dons_courses_hippiques(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    label = "Réduction d'impôt pour dons au profit des comités d'organisation des courses hippiques"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return ceil(
            0.5 * min_(
                ceil(foyer_fiscal("revenu_net_global_imposable", period) * .15),  # TODO: parameters
                foyer_fiscal("dons_courses_hippiques", period)
            )
        )

class versements_promotion_exportation(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    cerfa_field = "YK"
    label = "Versements au profit de la promotion de manifestations commerciales en vue de favoriser l'export des entreprises calédoniennes"
    definition_period = YEAR


class reduction_versements_promotion_exportation(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    label = "Réduction d'impôt pour versements au profit de la promotion de manifestations commerciales en vue de favoriser l'export des entreprises calédoniennes"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        reduction = ceil(
            0.5 * min_(
                ceil(foyer_fiscal("revenu_net_global_imposable", period) * .15),  # TODO: parameters
                foyer_fiscal("versements_promotion_exportation", period)
            )
        )
        resident = foyer_fiscal("resident", period)
        return where(resident, reduction, 0)


class souscription_via_plateforme_de_financement_participatif(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    cerfa_field = "YT"
    label = "Souscription au capital de sociétés par le biais d'une plateforme de financement participatif"
    definition_period = YEAR


class reduction_souscription_via_plateforme_de_financement_participatif(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    label = "Réduction d'impôt pour souscription au capital de sociétés par le biais d'une plateforme de financement participatif"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        reduction = ceil(
            0.5 * min_(
                3_000_000,  # TODO: parameters
                foyer_fiscal("souscription_via_plateforme_de_financement_participatif", period)
            )
        )
        resident = foyer_fiscal("resident", period)
        return where(resident, reduction, 0)

# Réductions d'impôts pour investissement locatif

class investissement_immeuble_neuf_habitation_principale(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    cerfa_field = "YH"
    label = "Investissement dans un immeuble neuf en NC acquis ou construit à usage d'habitation principale"
    definition_period = YEAR


class investissement_immeubles_neufs_acquis_loues_nus_habitation_principale(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    cerfa_field = "YI"
    label = "Investissement dans des immeubles neufs acquis en NC destinés exclusivement à être loués nus à usage d'habitation principale"
    definition_period = YEAR


class reduction_investissement_locatif(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    label = "Réduction d'impôt pour investissement locatif"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        montant_investi = (
            foyer_fiscal("investissement_immeuble_neuf_habitation_principale", period)
            + foyer_fiscal(
                "investissement_immeubles_neufs_acquis_loues_nus_habitation_principale",
                period,
            )
        )
        reduction = min_(ceil(montant_investi), 5_400_000)
        resident = foyer_fiscal("resident", period)
        return where(resident, reduction, 0)


## Réductions d'impôts des entreprises


class dons_organismes_aide_pme(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    cerfa_field = "YR"
    label = "Dons en faveur des organismes venant en aide aux PME"
    definition_period = YEAR


class reduction_dons_organismes_aide_pme(Variable):
    unit = "currency"
    value_type = int
    entity = FoyerFiscal
    label = "Réduction d'impôt pour dons en faveur des organismes venant en aide aux PME"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        plafond = ceil(foyer_fiscal("revenu_net_global_imposable", period) * .15)  # TODO: parameters
        reduction = ceil(min_(foyer_fiscal("dons_organismes_aide_pme", period), plafond) * .75)  # TODO: parameters
        resident = foyer_fiscal("resident", period)
        return where(resident, reduction, 0)


# TODO: cases YE YF nontrouvées dans déclarations
