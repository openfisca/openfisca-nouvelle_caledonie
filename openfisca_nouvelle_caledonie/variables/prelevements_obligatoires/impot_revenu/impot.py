"""Calcul de l'impôt sur le revenu."""

from numpy import floor

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal


class revenu_brut_global(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Revenu brut global"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        revenus_categoriels_tspr = foyer_fiscal(
            "revenus_categoriels_tspr", period
        )  #     // pension    #     // "REVENUS_FONCIERS" est egal a "AA"
        revenu_categoriel_foncier = foyer_fiscal("revenus_fonciers_soumis_ir", period)
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
    value_type = float
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

    def formula(foyer_fiscal, period):
        return where(
            foyer_fiscal("resident", period),
            (
                foyer_fiscal("enfants_accueillis", period) * 406_000  # TODO: parameters
                + foyer_fiscal("enfants_accueillis_handicapes", period) * 540_000
            ),
            0,
        )


class revenu_net_global_imposable(Variable):
    value_type = float
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
    value_type = float
    entity = FoyerFiscal
    label = "Impot brut"
    definition_period = YEAR

    def formula_2016(foyer_fiscal, period, parameters):

        # from tmp/engine/rules/_2008/impots/ImpotBrutUtil2008.java
        tauxPart1 = 8 / 100

        taux_moyen_imposition_non_resident = foyer_fiscal(
            "taux_moyen_imposition_non_resident", period
        )

        # Calcul de l'impôt brut pour les résidents

        parts_fiscales = foyer_fiscal("parts_fiscales", period)
        revenu_non_imposable = foyer_fiscal("revenu_non_imposable", period)
        revenu_net_global_imposable = foyer_fiscal(
            "revenu_net_global_imposable", period
        )

        parts_fiscales_reduites = foyer_fiscal("parts_fiscales_reduites", period)

        revenu_par_part = (
            max_(revenu_net_global_imposable, 0) + revenu_non_imposable
        ) / parts_fiscales

        revenu_par_part_reduite = (
                max_(revenu_net_global_imposable, 0) + revenu_non_imposable
            ) / parts_fiscales_reduites

        bareme = parameters(period).prelevements_obligatoires.impot_revenu.bareme

        impot_brut_complet = bareme.calc(revenu_par_part) * parts_fiscales
        impot_brut_reduit = bareme.calc(revenu_par_part_reduite) * parts_fiscales_reduites

        # Au final, l'impôt brut est une fraction du résultat précédent
        revenu_total = where(revenu_net_global_imposable > 0, revenu_net_global_imposable + revenu_non_imposable, 1)
        fraction = where(revenu_net_global_imposable > 0, revenu_net_global_imposable / revenu_total, 1)

        impot_brut_complet = where(impot_brut_complet > 0, impot_brut_complet, 0)
        impot_brut_complet = where(
            fraction < 0.01,  # TODO: parameters
            0,
            impot_brut_complet * fraction,
        )

        impot_brut_reduit = where(impot_brut_reduit > 0, impot_brut_reduit, 0)
        impot_brut_reduit = where(
            fraction < 0.01,  # TODO: parameters
            0,
            impot_brut_reduit * fraction,
        )

        impot_brut = max_(impot_brut_complet, impot_brut_reduit - ((parts_fiscales - parts_fiscales_reduites) * 2 * 300000))  # TODO: parameters

        # L'impôt brut est plafonné à 50% des revenus
        taux_plafond = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.taux_plafond
        impot_brut_resident = min_(
            taux_plafond * revenu_net_global_imposable, impot_brut
        )

        # Calcul de l'impôt brut Non résident
        revenu_brut_global = foyer_fiscal("revenu_brut_global", period)
        den = where(
            revenu_brut_global == 0,
            1,
            revenu_brut_global,
        )
        interets_de_depots = foyer_fiscal("interets_de_depots", period)
        pourcentage = (
            where(
                revenu_brut_global == 0,
                0,
                interets_de_depots,  # case BB
            )
            / den
        )
        # //  TxNI= 25 % si case 46 = 1 et case 47 =vide
        txNI = where(
            taux_moyen_imposition_non_resident > 0,
            taux_moyen_imposition_non_resident,
            0.25,
        )
        # // 8% x RNGI x pourcentage
        part1 = (
            tauxPart1 * revenu_net_global_imposable * pourcentage
        )  # // txNI x rngi x (1 - pourcentage)
        part2 = txNI * revenu_net_global_imposable * (1 - pourcentage)
        # Résultat pour les non résidents
        impot_brut_non_resident = part1 + part2

        return where(
            foyer_fiscal("resident", period),
            impot_brut_resident,
            impot_brut_non_resident,
        )

    def formula_2008(foyer_fiscal, period, parameters):
        # from tmp/engine/rules/_2008/impots/ImpotBrutUtil2008.java
        tauxPart1 = 8 / 100

        taux_moyen_imposition_non_resident = foyer_fiscal(
            "taux_moyen_imposition_non_resident", period
        )

        # Calcul de l'impôt brut pour les résidents

        parts_fiscales = foyer_fiscal("parts_fiscales", period)
        revenu_non_imposable = foyer_fiscal("revenu_non_imposable", period)
        revenu_net_global_imposable = foyer_fiscal(
            "revenu_net_global_imposable", period
        )

        revenu_par_part = (
            max_(revenu_net_global_imposable, 0) + revenu_non_imposable
        ) / parts_fiscales

        bareme = parameters(period).prelevements_obligatoires.impot_revenu.bareme

        impot_brut = bareme.calc(revenu_par_part) * parts_fiscales

        # Au final, l'impôt brut est une fraction du résultat précédent
        revenu_total = where(revenu_net_global_imposable > 0, revenu_net_global_imposable + revenu_non_imposable, 1)
        fraction = where(revenu_net_global_imposable > 0, revenu_net_global_imposable / revenu_total, 1)

        impot_brut = where(impot_brut > 0, impot_brut, 0)
        impot_brut = where(
            fraction < 0.01,  # TODO: parameters
            0,
            impot_brut * fraction,
        )

        # L'impôt brut est plafonné à 50% des revenus
        taux_plafond = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.taux_plafond
        impot_brut_resident = min_(
            taux_plafond * revenu_net_global_imposable, impot_brut
        )

        # Calcul de l'impôt brut Non résident
        revenu_brut_global = foyer_fiscal("revenu_brut_global", period)
        den = where(
            revenu_brut_global == 0,
            1,
            revenu_brut_global,
        )
        interets_de_depots = foyer_fiscal("interets_de_depots", period)
        pourcentage = (
            where(
                revenu_brut_global == 0,
                0,
                interets_de_depots,  # case BB
            )
            / den
        )
        # //  TxNI= 25 % si case 46 = 1 et case 47 =vide
        txNI = where(
            taux_moyen_imposition_non_resident > 0,
            taux_moyen_imposition_non_resident,
            0.25,
        )

        # // 8% x RNGI x pourcentage
        part1 = (
            tauxPart1 * revenu_net_global_imposable * pourcentage
        )  # // txNI x rngi x (1 - pourcentage)
        part2 = txNI * revenu_net_global_imposable * (1 - pourcentage)
        # Résultat pour les non résidents
        impot_brut_non_resident = part1 + part2

        return where(
            foyer_fiscal("resident", period),
            impot_brut_resident,
            impot_brut_non_resident,
        )


#  Permet de recalculer l'impôt supplémentaire dû à un salaire différé ou à une pension différée. Il se base sur la calcul de l'impôt brut
#
#  if (quotient != null) {
#     rngiRevise = arrondit1000(RevenuNetGlobalImposable) + quotient
#     impotBrutRevise = calculImpotBrut(rngiRevise)
#     retun impotBrutRevise - ImpotBrut * nbAnnee;


class imputations(Variable):
    value_type = float
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
            impot_apres_imputations - 5_000,
            foyer_fiscal("reductions_impot", period),
        )

        return max_(impot_brut - reductions_palfonnees, 0)


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
    value_type = float
    entity = FoyerFiscal
    label = "Impot net"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        impot_apres_reductions = foyer_fiscal("impot_apres_reductions", period)
        credits_impot = foyer_fiscal("credits_impot", period)
        plus_values_professionnelles = foyer_fiscal(
            "plus_values_professionnelles", period
        )

        return impot_apres_reductions - credits_impot + plus_values_professionnelles
