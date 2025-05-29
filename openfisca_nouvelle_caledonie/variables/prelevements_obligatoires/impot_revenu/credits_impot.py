"""Réductions d'impots."""

import numpy as np

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal

# Cadre 14 Autres réductions et crédits d'impôt

## Crédits et réductions d'impôts des entreprises


class dons_organismes_aide_pme(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YH"
    label = "Dons en faveur des organismes venant en aide aux PME"
    definition_period = YEAR


class depenses_exportation(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "WX"
    label = "Dépenses à l'exportation"
    definition_period = YEAR


class investissement_productif_industriel(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YQ"
    label = "Investissement productif industriel"
    definition_period = YEAR


class souscription_fcp(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YV"
    label = "Souscription à un fonds commun de placement en Nouvelle-Calédonie"
    definition_period = YEAR


class depenses_recherche_innovation(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YS"
    label = "Dépenses de recherche et d'innovation"
    definition_period = YEAR


class mecenat_entreprise(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YX"
    label = "Mécénat d'entreprise"
    definition_period = YEAR


class creche_entreprise(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YG"
    label = "Crèche d'entreprise"
    definition_period = YEAR


## Autres crédits d'impôts


class investissements_agrees_noumea_etc(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YO"
    label = "Investissement agréés à Nouméa, Dumbéa, Mont-dore et Païta (hors îlots)"
    definition_period = YEAR


class investissements_agrees_autres(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YP"
    label = "Investissement agréés hors Nouméa, Dumbéa, Mont-dore et Païta (îlots)"
    definition_period = YEAR


class investissements_agrees_mixtes(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YZ"
    label = "Investissement agréés mixtes"
    definition_period = YEAR


class solde_investissements_agrees_noumea_etc(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "WA"
    label = "Report du solde des investissements agréés à Nouméa, Dumbéa, Mont-dore et Païta (hors îlots)"
    definition_period = YEAR


class solde_investissements_agrees_autres(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "WB"
    label = "Report du solde des investissements agréés hors Nouméa, Dumbéa, Mont-dore et Païta (îlots)"
    definition_period = YEAR


class credits_impot(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Crédits d'impôt"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        impot_apres_reductions = foyer_fiscal("impot_apres_reductions", period)

        solde_investissements_agrees = foyer_fiscal(
            "solde_investissements_agrees_noumea_etc", period
        ) + foyer_fiscal("solde_investissements_agrees_autres", period)

        credits_investissement = (
            foyer_fiscal("investissements_agrees_noumea_etc", period)
            + foyer_fiscal("investissements_agrees_autres", period)
            + foyer_fiscal("investissements_agrees_mixtes", period)
            + solde_investissements_agrees
        )

        # Calcul des plafonds
        plaf_70 = where(
            credits_investissement > 0,
            np.ceil(0.70 * impot_apres_reductions),
            0,  # TODO: parameters
        )

        investissement_productif_industriel = foyer_fiscal(
            "investissement_productif_industriel", period
        )
        plaf_50 = where(
            investissement_productif_industriel > 0,
            np.ceil(0.50 * impot_apres_reductions),  # TODO: parameters
            0,
        )  # TOD0: manque case WE https://github.com/openfisca/openfisca-nouvelle_caledonie/issues/34

        souscription_fcp = foyer_fiscal("souscription_fcp", period)
        plaf_60 = where(
            souscription_fcp > 0,
            np.ceil(0.60 * impot_apres_reductions),  # TODO: parameters
            0,
        )  # TOD0: manque case WW https://github.com/openfisca/openfisca-nouvelle_caledonie/issues/34

        mecenat_creche = foyer_fiscal("mecenat_entreprise", period) + foyer_fiscal(
            "creche_entreprise", period
        )
        plaf_100 = where(
            mecenat_creche > 0,
            impot_apres_reductions,
            0,
        )

        # L'ensemble des crédits d'impôt ne peut dépasser le plus grand plafond
        plafond_credits = np.maximum.reduce([plaf_50, plaf_70, plaf_60, plaf_100])

        # Crédits d'impôt pour les reports de solde d'investissement
        solde_investissement_plafonnes = min_(solde_investissements_agrees, plaf_70)
        retenue = min_(solde_investissement_plafonnes, plafond_credits)

        # retenue_wa
        credit_solde_noumea_etc = where(
            solde_investissement_plafonnes > 0,
            np.ceil(
                (
                    foyer_fiscal("solde_investissements_agrees_noumea_etc", period)
                    * retenue
                )
                / solde_investissements_agrees
            ),
            0,
        )
        # retenue_wb
        credit_solde_autres = where(
            solde_investissement_plafonnes > 0,
            np.ceil(
                (foyer_fiscal("solde_investissements_agrees_autres", period) * retenue)
                / solde_investissements_agrees
            ),
            0,
        )

        reliquat_plafond_credits = max_(
            plafond_credits - credit_solde_noumea_etc - credit_solde_autres,
            0,
        )

        # report
        report_solde_investissements_agrees_net = max_(
            (solde_investissements_agrees - plaf_70),
            0,
        )

        # report_yo
        # report_investissements_agrees_noumea
        _ = where(
            solde_investissements_agrees > 0,
            (
                foyer_fiscal("investissements_agrees_noumea_etc", period)
                * report_solde_investissements_agrees_net
                / solde_investissements_agrees
            ),
            0,
        )

        # report wb
        report_investissements_agrees_noumea = where(
            solde_investissements_agrees > 0,
            (
                foyer_fiscal("solde_investissements_agrees_autres", period)
                * report_solde_investissements_agrees_net
                / solde_investissements_agrees
            ),
            0,
        )

        # On reporte le reste sur les autres crédits d'impôt pour investissement     # On reporte le reste sur les autres crédits d'impôt pour investissement
        credits_investissement_restants = np.ceil(
            foyer_fiscal("investissements_agrees_noumea_etc", period)
            + foyer_fiscal("investissements_agrees_autres", period)
        ) + np.ceil(foyer_fiscal("investissements_agrees_mixtes", period))
        reliquet_credits_investissement_restants_plafonnes = min_(
            min_(
                credits_investissement_restants,
                plaf_70,
            ),
            reliquat_plafond_credits,
        )

        # retenu_yo
        credit_investissements_agrees_noumea_etc = np.ceil(
            where(
                foyer_fiscal("investissements_agrees_noumea_etc", period) > 0,
                (
                    foyer_fiscal("investissements_agrees_noumea_etc", period)
                    * reliquet_credits_investissement_restants_plafonnes
                    / credits_investissement_restants,
                ),
                0,
            )
        )

        # retenu_yp
        credit_investissements_agrees_autres = np.ceil(
            where(
                foyer_fiscal("investissements_agrees_autres", period) > 0,
                (
                    foyer_fiscal("investissements_agrees_autres", period)
                    * reliquet_credits_investissement_restants_plafonnes
                    / credits_investissement_restants
                ),
                0,
            )
        )

        # retenu_yz
        credit_investissements_agrees_mixtes = np.ceil(
            where(
                foyer_fiscal("investissements_agrees_mixtes", period) > 0,
                (
                    foyer_fiscal("investissements_agrees_mixtes", period)
                    * reliquet_credits_investissement_restants_plafonnes
                    / credits_investissement_restants
                ),
                0,
            )
        )

        # retenu_yz
        credit_investissements_agrees_mixtes = where(
            foyer_fiscal("investissements_agrees_mixtes", period) > 0,
            reliquet_credits_investissement_restants_plafonnes
            - credit_investissements_agrees_noumea_etc
            - credit_investissements_agrees_autres,
            credit_investissements_agrees_mixtes,
        )

        # retenue yp
        credit_investissements_agrees_autres = where(
            (
                (foyer_fiscal("investissements_agrees_autres", period) > 0)
                & (foyer_fiscal("investissements_agrees_mixtes", period) == 0)
            ),
            (
                reliquet_credits_investissement_restants_plafonnes
                - credit_investissements_agrees_noumea_etc,
            ),
            credit_investissements_agrees_autres,
        )

        reliquat_plafond_credits = max_(
            (
                reliquat_plafond_credits
                - credit_investissements_agrees_autres
                - credit_investissements_agrees_mixtes
            ),
            0,
        )
        report_investissements = where(
            credits_investissement_restants > plaf_70,
            credits_investissement_restants - plaf_70,
            report_investissements_agrees_noumea,
        )
        report_investissements_agrees_noumea = report_investissements

        # Amortissements excedentaires WE TODO; à vérifer et inclure
        # credit_we
        _ = where(
            solde_investissement_plafonnes > 0,
            np.ceil(
                (
                    foyer_fiscal("solde_investissements_agrees_noumea_etc", period)
                    * retenue
                )
                / solde_investissements_agrees
            ),
            0,
        )

        # RETENUE_WE = min(we, plaf_we
        # RETENUE_W       = min(RETENUE_WE, plaf_credits)
        # plaf_credits = plaf_credits - RETEUE_WE
        # REPORT_WE  we) - plaf_we if we) > plaf_we else
        # # YW
        # RETENUE_YW = min(yw, plaf_yw)
        # RETENUE_YW = min(RETENUE_YW, plaf_credits)
        # plaf_credits = plaf_credits - RETENUE_W
        # REPORT_YW = max(yw) - RETENUE_YW, 0

        # YQ
        credit_investissement_productif_industriel = min_(
            min_(
                0.15
                * foyer_fiscal(
                    "investissement_productif_industriel", period
                ),  # TODO: parameters
                plaf_50,
            ),
            reliquat_plafond_credits,
        )

        reliquat_plafond_credits = max_(
            reliquat_plafond_credits - reliquat_plafond_credits,
            0,
        )
        # REPORT_YQ = retenue - plaf_yq if retenue > plaf_yq else
        # YV
        credit_souscription_fcp = min_(
            min_(
                0.15 * souscription_fcp,
                plaf_50,
            ),
            reliquat_plafond_credits,
        )
        reliquat_plafond_credits = max_(
            reliquat_plafond_credits - credit_souscription_fcp,
            0,
        )
        # report_yv
        _ = max_(
            (credit_souscription_fcp - plaf_50),
            0,
        )
        credits_totaux = (
            credit_solde_noumea_etc
            + credit_solde_autres
            + credit_investissements_agrees_noumea_etc
            + credit_investissements_agrees_autres
            + credit_investissements_agrees_mixtes
            + credit_investissement_productif_industriel
            + credit_souscription_fcp
            # + credit_we
        )

        # YG
        credit_creche_entreprise = min_(
            0.50
            * min_(  # TODO: parameters
                foyer_fiscal("creche_entreprise", period),
                120_000_000,  # TODO: parameters
            ),
            60_000_000,  # TODO: parameters
        )
        credit_creche_entreprise = min_(
            credit_creche_entreprise,
            impot_apres_reductions - credits_totaux,
        )

        reliquat_plafond_credits = max_(
            reliquat_plafond_credits - credit_creche_entreprise,
            0,
        )

        # YX
        credit_mecenat_entreprise = where(
            foyer_fiscal("resident", period),
            min_(
                np.ceil(0.80 * foyer_fiscal("mecenat_entreprise", period)),
                impot_apres_reductions - credits_totaux,
            ),
            0,
        )

        reliquat_plafond_credits = max_(
            reliquat_plafond_credits - credit_mecenat_entreprise,
            0,
        )

        # WX
        credit_depenses_exportation = where(
            foyer_fiscal("resident", period),
            min_(
                foyer_fiscal("depenses_exportation", period),
                (impot_apres_reductions - credit_mecenat_entreprise - credits_totaux),
            ),
            0,
        )

        # YS
        credit_depenses_recherche_innovation = where(
            foyer_fiscal("resident", period),
            min_(
                foyer_fiscal("depenses_recherche_innovation", period),
                (
                    impot_apres_reductions
                    - credit_mecenat_entreprise
                    - credit_depenses_exportation
                    - credits_totaux
                ),
            ),
            0,
        )

        return (
            credit_solde_noumea_etc
            + credit_solde_autres
            + credit_investissements_agrees_noumea_etc
            + credit_investissements_agrees_autres
            + credit_investissements_agrees_mixtes
            + credit_investissement_productif_industriel
            + credit_souscription_fcp
            # + credit_we
            + credit_mecenat_entreprise
            + credit_depenses_exportation
            + credit_depenses_recherche_innovation,
        )
