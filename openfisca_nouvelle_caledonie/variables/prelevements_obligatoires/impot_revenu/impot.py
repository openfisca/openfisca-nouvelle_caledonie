"""Calcul de l'impôt sur le revenu."""

from numpy import floor

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal


class revenu_brut_global(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Revenu brut global"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        revenus_categoriels_tspr = foyer_fiscal(
            "revenus_categoriels_tspr", period
        )  #     // pension    #     // "REVENUS_FONCIERS" est egal a "AA"
        revenu_categoriel_foncier = foyer_fiscal("revenu_categoriel_foncier", period)
        revenu_categoriel_capital = foyer_fiscal("revenu_categoriel_capital", period)
        revenus_categoriels_non_salarie = foyer_fiscal(
            "revenu_categoriel_non_salarie", period
        )

        return (
            revenus_categoriels_tspr
            + revenu_categoriel_capital
            + revenu_categoriel_foncier
            + revenus_categoriels_non_salarie
            # TODO: revenu_categoriel_plus_values
        )


class revenu_non_imposable(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Revenu non imposable"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return where(
            foyer_fiscal("resident", period),
            foyer_fiscal("revenus_de_source_exterieur", period),
            0,
        )


class abattement_enfants_accueillis(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Abattement enfants accueillis"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        abattements = parameters(period).prelevements_obligatoires.impot_revenu.abattements
        return where(
            foyer_fiscal("resident", period),
            (
                foyer_fiscal("enfants_accueillis", period) *
                abattements.abattement_enfants_accueillis
                + foyer_fiscal("enfants_accueillis_handicapes", period) *
                abattements.abattement_enfants_accueillis_handicape
            ),
            0,
        )


class revenu_net_global_imposable(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Revenu net global imposable"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        rngi = max_(
            (
                foyer_fiscal("revenu_brut_global", period)
                - foyer_fiscal("charges_deductibles", period)
                + foyer_fiscal("deductions_reintegrees", period)
                - foyer_fiscal("abattement_enfants_accueillis", period)
            ),
            0,
        )
        return floor(rngi / 1000) * 1000  # Arrondi à la baisse par tranche de 1000


class impot_brut(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Impot brut"
    definition_period = YEAR

    def formula_2016(foyer_fiscal, period, parameters):
        revenu_net_global_imposable = foyer_fiscal("revenu_net_global_imposable", period)
        impot_brut_avant_quotient = foyer_fiscal("impot_brut_avant_quotient", period)
        total = impot_brut_avant_quotient * 1.0
        roles = [FoyerFiscal.DECLARANT_PRINCIPAL, FoyerFiscal.CONJOINT]

        for role in roles:
            rngi = floor(
                (
                    revenu_net_global_imposable
                    + foyer_fiscal.sum(
                        foyer_fiscal.members("salaire_differe_apres_deduction", period),
                        role=role
                        )
                    ) / 1000) * 1000  # Arrondi à la baisse par tranche de 1000
            annees_de_rappel_salaires = foyer_fiscal.sum(
                foyer_fiscal.members("annees_de_rappel_salaires", period),
                role=role
            )
            impot_brut_apres_salaires_differes = calcul_impot_brut_2016(
                foyer_fiscal, period, parameters, rngi = rngi
                )
            impot_supplementaire_salaires_differes = (
                impot_brut_apres_salaires_differes - impot_brut_avant_quotient
            ) * annees_de_rappel_salaires

            rngi = floor(
                (
                    revenu_net_global_imposable
                    + foyer_fiscal.sum(
                        foyer_fiscal.members("pensions_differes_apres_deduction", period),
                        role=role
                        )
                    ) / 1000) * 1000  # Arrondi à la baisse par tranche de 1000
            annees_de_rappel_pensions = foyer_fiscal.sum(
                foyer_fiscal.members("annees_de_rappel_pensions", period),
                role=role
            )
            impot_brut_apres_pensions_differes = calcul_impot_brut_2016(
                foyer_fiscal, period, parameters, rngi = rngi
            )
            impot_supplementaire_pensions_differes = (
                impot_brut_apres_pensions_differes - impot_brut_avant_quotient
            ) * annees_de_rappel_pensions

            total += (
                impot_supplementaire_salaires_differes
                + impot_supplementaire_pensions_differes
                )

        return total

class impot_brut_avant_quotient(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Impot brut avant revenu différé"
    definition_period = YEAR

    def formula_2016(foyer_fiscal, period, parameters):
        return calcul_impot_brut_2016(foyer_fiscal, period, parameters)

    def formula_2008(foyer_fiscal, period, parameters):
        return calcul_impot_brut_2008_2015(foyer_fiscal, period, parameters)


class imputations(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Imputations"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return (
            foyer_fiscal("ircdc_impute", period)
            + foyer_fiscal("irvm_impute", period)
            + foyer_fiscal("retenue_a_la_source_metropole_imputee", period)
        )


class impot_apres_reductions(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Impot net"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        impot_brut = foyer_fiscal("impot_brut", period)
        impot_apres_imputations = max_(
            impot_brut - foyer_fiscal("imputations", period), 0
        )
        reductions_palfonnees = min_(
                max_(impot_apres_imputations - 5_000, 0),
                foyer_fiscal("reductions_impot", period),
            )

        return max_(impot_apres_imputations - reductions_palfonnees, 0)


class resident(Variable):
    value_type = bool
    default_value = True
    entity = FoyerFiscal
    label = "Foyer fiscal résident en Nouvelle Calédonie"
    definition_period = YEAR


class taux_moyen_imposition_non_resident(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Taux moyen d'imposiition du non résident"
    definition_period = YEAR


class impot_net(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Impot net"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        impot_apres_reductions = foyer_fiscal("impot_apres_reductions", period)
        credits_impot = foyer_fiscal("credits_impot", period)
        plus_values_professionnelles = foyer_fiscal(
            "plus_values_professionnelles", period
        )
        reduction_impots_reintegrees = foyer_fiscal("reduction_impots_reintegrees", period)

        return floor(
            impot_apres_reductions - credits_impot + plus_values_professionnelles + reduction_impots_reintegrees
        )


class penalites(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Pénalités"
    definition_period = YEAR

    # TODO: faut-il faire une formule avec 10% de pénalité


class impot_et_ccs_apres_penalites(Variable):
    value_type = int
    entity = FoyerFiscal
    label = "Impot + CCS net des pénalités"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        impot_net = foyer_fiscal("impot_net", period)
        ccs_revenu_du_capital = foyer_fiscal("ccs_revenu_du_capital", period)
        penalites = foyer_fiscal("penalites", period)
        return round_(impot_net + penalites + ccs_revenu_du_capital)


# Helpers

def calcul_impot_brut_2016(foyer_fiscal, period, parameters, rngi = None):
    """Calcul de l'impôt brut pour les résidents et non-résidents pour la période 2016 et suivantes."""
    return floor(
        where(
            foyer_fiscal("resident", period),
            calcul_impot_brut_resident_2016(foyer_fiscal, period, parameters, rngi),
            calcul_impot_brut_non_resident(foyer_fiscal, period),
        )
    )


def calcul_impot_brut_2008_2015(foyer_fiscal, period, parameters, rngi_variable_name = "revenu_net_global_imposable"):
    """Calcul de l'impôt brut pour les résidents et non-résidents pour les périodes 2008-2015."""
    return floor(
        where(
            foyer_fiscal("resident", period),
            calcul_impot_brut_resident_2008_2015(foyer_fiscal, period, parameters, rngi_variable_name),
            calcul_impot_brut_non_resident(foyer_fiscal, period),
        )
    )

def calcul_impot_brut_non_resident(foyer_fiscal, period):
    """Calcul de l'impôt brut pour les non-résidents."""
    taux_moyen_imposition_non_resident = foyer_fiscal(
        "taux_moyen_imposition_non_resident", period
    )
    revenu_brut_global = foyer_fiscal("revenu_brut_global", period)
    revenu_net_global_imposable = foyer_fiscal(
        "revenu_net_global_imposable", period
    )
    interets_de_depots = foyer_fiscal("interets_de_depots", period)
    pourcentage = interets_de_depots / (revenu_brut_global + 1 * (revenu_brut_global == 0))
        # //  TxNI= 25 % si case 46 = 1 et case 47 =vide
    txNI = where(
        taux_moyen_imposition_non_resident > 0,
        taux_moyen_imposition_non_resident,
        0.25, # TODO: parameters
    )
    tauxPart1 = 8 / 100  # TODO: parameters
    # // 8% x RNGI x pourcentage
    part1 = (
        tauxPart1 * revenu_net_global_imposable * pourcentage
    )  # // txNI x rngi x (1 - pourcentage)
    part2 = txNI * revenu_net_global_imposable * (1 - pourcentage)

    return part1 + part2


def calcul_impot_brut_resident_2016(foyer_fiscal, period, parameters, rngi = None):
    """Calcul de l'impôt brut pour les résidents pour la période 2016 et suivantes."""
    if rngi is None:
        revenu_net_global_imposable = foyer_fiscal(
            "revenu_net_global_imposable", period
        )
    else:
        revenu_net_global_imposable = rngi

    parts_fiscales = foyer_fiscal("parts_fiscales", period)
    revenu_non_imposable = foyer_fiscal("revenu_non_imposable", period)
    parts_fiscales_reduites = foyer_fiscal("parts_fiscales_reduites", period)

    revenu_par_part = (parts_fiscales > 0) * floor(
        (max_(revenu_net_global_imposable, 0) + revenu_non_imposable)
        / (parts_fiscales + (parts_fiscales == 0))
    )
    revenu_par_part_reduite = (parts_fiscales_reduites > 0) * floor(
        (max_(revenu_net_global_imposable, 0) + revenu_non_imposable)
        / (parts_fiscales_reduites + (parts_fiscales_reduites == 0))
    )

    bareme = parameters(period).prelevements_obligatoires.impot_revenu.bareme
    impot_brut_complet = bareme.calc(revenu_par_part) * parts_fiscales
    impot_brut_reduit = (
        bareme.calc(revenu_par_part_reduite) * parts_fiscales_reduites
    )

    # Au final, l'impôt brut est une fraction du résultat précédent
    revenu_total = where(
        revenu_net_global_imposable > 0,
        revenu_net_global_imposable + revenu_non_imposable,
        1,
    )
    fraction = where(
        revenu_net_global_imposable > 0,
        revenu_net_global_imposable / revenu_total,
        1,
    )

    impot_brut_complet = where(impot_brut_complet > 0, impot_brut_complet, 0)

    part_minimale = parameters(
        period
    ).prelevements_obligatoires.impot_revenu.part_min_revenu_total_imposable
    impot_brut_complet = where(
        fraction < part_minimale,
        0,
        impot_brut_complet * fraction,
    )
    impot_brut_reduit = where(impot_brut_reduit > 0, impot_brut_reduit, 0)
    impot_brut_reduit = where(
        fraction < part_minimale,
        0,
        impot_brut_reduit * fraction,
    )
    # Plafonnement du quotient familial

    plafond_quotient_familial = parameters(period).prelevements_obligatoires.impot_revenu.plafond_quotient_familial
    impot_brut = max_(
        impot_brut_complet,
        impot_brut_reduit
        - ((parts_fiscales - parts_fiscales_reduites) * 2 * plafond_quotient_familial),
    )

    # L'impôt brut est plafonné à 50% des revenus
    taux_plafond = parameters(
        period
    ).prelevements_obligatoires.impot_revenu.taux_plafond
    return min_(
        taux_plafond * revenu_net_global_imposable, impot_brut
    )


def calcul_impot_brut_resident_2008_2015(foyer_fiscal, period, parameters, rngi):
    """Calcul de l'impôt brut pour les résidents pour les périodes 2008-2015."""
    # Les résidents ont par définition on des parts fiscales non nulles
    if rngi is None:
        revenu_net_global_imposable = foyer_fiscal("revenu_net_global_imposable", period)
    else:
        revenu_net_global_imposable = rngi

    parts_fiscales = foyer_fiscal("parts_fiscales", period)
    revenu_non_imposable = foyer_fiscal("revenu_non_imposable", period)

    revenu_par_part = (parts_fiscales > 0) * floor(
        (max_(revenu_net_global_imposable, 0) + revenu_non_imposable)
        / (parts_fiscales + (parts_fiscales == 0))
    )

    bareme = parameters(period).prelevements_obligatoires.impot_revenu.bareme
    impot_brut = bareme.calc(revenu_par_part) * parts_fiscales

    # Au final, l'impôt brut est une fraction du résultat précédent
    revenu_total = where(
        revenu_net_global_imposable > 0,
        revenu_net_global_imposable + revenu_non_imposable,
        1,
    )

    fraction = where(
        revenu_net_global_imposable > 0,
        revenu_net_global_imposable / revenu_total,
        1,
    )
    impot_brut = where(impot_brut > 0, impot_brut, 0)

    part_minimale = parameters(
        period
    ).prelevements_obligatoires.impot_revenu.part_min_revenu_total_imposable
    impot_brut = where(
        fraction < part_minimale,
        0,
        impot_brut * fraction,
    )

    # L'impôt brut est plafonné à 50% des revenus
    taux_plafond = parameters(
        period
    ).prelevements_obligatoires.impot_revenu.taux_plafond
    return min_(
        taux_plafond * revenu_net_global_imposable, impot_brut
    )
