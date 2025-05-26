"""Calcul de l'impôt sur le revenu."""

import numpy as np
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
        return floor(rngi / 1000) * 1000


class impot_brut(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Impot brut"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        # from tmp/engine/rules/_2008/impots/ImpotBrutUtil2008.java
        tauxPart1 = 8 / 100

        taux_moyen_imposition_non_resident = foyer_fiscal(
            "taux_moyen_imposition_non_resident", period
        )

        # Calcul de l'impôt brut pour les résidents

        nombre_de_parts = foyer_fiscal("parts_fiscales", period)
        revenu_non_imposable = foyer_fiscal("revenu_non_imposable", period)
        revenu_net_global_imposable = foyer_fiscal(
            "revenu_net_global_imposable", period
        )

        revenu_par_part = (
            max_(revenu_net_global_imposable, 0) + revenu_non_imposable
        ) / nombre_de_parts

        bareme = parameters(period).prelevements_obligatoires.impot_revenu.bareme

        impot_brut = bareme.calc(revenu_par_part) * nombre_de_parts

        # Au final, l'impôt brut est une fraction du résultat précédent
        numerateur = revenu_net_global_imposable
        denominateur = where(numerateur > 0, numerateur + revenu_non_imposable, 1)
        fraction = where(numerateur > 0, numerateur / denominateur, 1)

        impot_brut = where(impot_brut > 0, impot_brut, 0)
        impot_brut = where(
            fraction < 0.01,  # TODO: à introduire dans les paramètres
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
        #     /// ----------------On applique les imputations----------------------------------------------------------
        #     resteImpotBrut = max(resteImpotBrut - zeroIfNull(outs.getTotalRetenueYAYBYC()), 0);

        #     // ----------------On applique les réductions-------------------------------------------------------------
        #     resteImpotBrut = max(resteImpotBrut - outs.getRetenueTotalRI(), 0);

        #     /// ----------------On applique les crédits d'impôt -----------------------------------------------------------

        #     double YX = zeroIfNull(ins.getYX());
        #     double WX = zeroIfNull(ins.getWX());
        #     double YS = zeroIfNull(ins.getYS());
        #     // Règles non applicable pour les non résidents
        #     if (!ins.isResident()) {
        #         YX = 0.0;
        #         WX = 0.0;
        #         YS = 0.0;
        #     }

        #     // Déduction des crédits d'impôt
        #     // Les plafonds se basent sur l'impot brut déduit des imputations et des réductions d'impôts
        #     // Donc les calculs avant
        #     double plaf_wawb = zeroIfNull(ins.getWA()) > 0 || zeroIfNull(ins.getWB()) > 0 ? ceil(TAUX_70 * resteImpotBrut) : 0;
        #     double plaf_yoypyz = zeroIfNull(ins.getYO()) > 0 || zeroIfNull(ins.getYP()) > 0 || zeroIfNull(ins.getYZ()) > 0 ? ceil(TAUX_70 * resteImpotBrut) : 0;
        #     double plaf_we = zeroIfNull(ins.getWE()) > 0 ? ceil(TAUX_50 * resteImpotBrut) : 0;
        #     double plaf_yw = zeroIfNull(ins.getYW()) > 0 ? ceil(TAUX_60 * resteImpotBrut) : 0;
        #     double plaf_yq = zeroIfNull(ins.getYQ()) > 0 ? ceil(TAUX_50 * resteImpotBrut) : 0;
        #     double plaf_yv = zeroIfNull(ins.getYV()) > 0 ? ceil(TAUX_60 * resteImpotBrut) : 0;
        #     double plaf_yx = YX > 0 ? resteImpotBrut : 0;
        #     double plaf_yg = zeroIfNull(ins.getYG()) > 0 ? resteImpotBrut : 0;
        #     // L'ensemble des crédits d'impot ne peut dépasser le plus grand plafond
        #     double plaf_credits = max(max(max(max(max(max(max(plaf_wawb, plaf_yoypyz), plaf_we), plaf_yw), plaf_yq), plaf_yv), plaf_yx), plaf_yg);
        #     // WA & WB
        #     double temp = zeroIfNull(ins.getWA()) + zeroIfNull(ins.getWB());
        #     double retenue = min(temp, plaf_wawb);
        #     retenue = min(retenue, plaf_credits);
        #     double den = temp == 0 ? 1 : temp;
        #     double RETENUE_WA = temp > 0 ? retenue * zeroIfNull(ins.getWA()) / den : 0;
        #     RETENUE_WA = ceil(RETENUE_WA);
        #     double RETENUE_WB = temp > 0 ? retenue * zeroIfNull(ins.getWB()) / den : 0;
        #     RETENUE_WB = ceil(RETENUE_WB);
        #     plaf_credits = plaf_credits - RETENUE_WA - RETENUE_WB;
        #     plaf_credits = max(plaf_credits, 0);
        #     // On reporte le reste ; WA sur YO
        #     double report = temp > plaf_wawb ? temp - plaf_wawb : 0;
        #     double REPORT_YO = temp > 0 ? zeroIfNull(ins.getWA()) * report / den : 0;
        #     double REPORT_WB = temp > 0 ? zeroIfNull(ins.getWB()) * report / den : 0;
        #     // YO & YP & YZ
        #     temp = ceil(zeroIfNull(ins.getYO()) + zeroIfNull(ins.getYP()) + ceil(zeroIfNull(ins.getYZ())));
        #     retenue = min(temp, plaf_yoypyz);
        #     retenue = min(retenue, plaf_credits);
        #     den = temp == 0 ? 1 : temp;
        #     double RETENUE_YO = temp > 0 ? retenue * zeroIfNull(ins.getYO()) / den : 0;
        #     RETENUE_YO = ceil(RETENUE_YO);
        #     double RETENUE_YP = retenue > 0 ? retenue * zeroIfNull(ins.getYP()) / den : 0;
        #     RETENUE_YP = ceil(RETENUE_YP);
        #     double RETENUE_YZ = retenue > 0 ? retenue * zeroIfNull(ins.getYZ()) / den : 0;
        #     RETENUE_YZ = ceil(RETENUE_YZ);
        #     // Correction des retenues pour que le total soit "retenue"
        #     RETENUE_YZ = zeroIfNull(ins.getYZ()) > 0 ? retenue - RETENUE_YP - RETENUE_YO : RETENUE_YZ;
        #     RETENUE_YP = zeroIfNull(ins.getYP()) > 0 && zeroIfNull(ins.getYZ()) == 0 ? retenue - RETENUE_YO : RETENUE_YP;
        #     plaf_credits = plaf_credits - RETENUE_YO - RETENUE_YP - RETENUE_YZ;
        #     report = temp > plaf_yoypyz ? temp - plaf_yoypyz : REPORT_YO;
        #     REPORT_YO = report;
        #     // WE
        #     double RETENUE_WE = min(zeroIfNull(ins.getWE()), plaf_we);
        #     RETENUE_WE = min(RETENUE_WE, plaf_credits);
        #     plaf_credits = plaf_credits - RETENUE_WE;
        #     double REPORT_WE = zeroIfNull(ins.getWE()) > plaf_we ? zeroIfNull(ins.getWE()) - plaf_we : 0;
        #     // YW
        #     double RETENUE_YW = min(zeroIfNull(ins.getYW()), plaf_yw);
        #     RETENUE_YW = min(RETENUE_YW, plaf_credits);
        #     plaf_credits = plaf_credits - RETENUE_YW;
        #     double REPORT_YW = max(zeroIfNull(ins.getYW()) - RETENUE_YW, 0);
        #     // YQ
        #     retenue = ceil(TAUX_15 * zeroIfNull(ins.getYQ()));
        #     double RETENUE_YQ = min(retenue, plaf_yq);
        #     RETENUE_YQ = min(retenue, plaf_credits);
        #     plaf_credits = plaf_credits - RETENUE_YQ;
        #     double REPORT_YQ = retenue > plaf_yq ? retenue - plaf_yq : 0;
        #     // YV
        #     retenue = ceil(TAUX_50 * zeroIfNull(ins.getYV()));
        #     double RETENUE_YV = min(retenue, plaf_yv);
        #     RETENUE_YV = min(retenue, plaf_credits);
        #     plaf_credits = plaf_credits - RETENUE_YV;
        #     double REPORT_YV = retenue > plaf_yv ? retenue - plaf_yv : 0;

        #     resteImpotBrut -= zeroIfNull(RETENUE_WA);
        #     resteImpotBrut -= zeroIfNull(RETENUE_WB);
        #     resteImpotBrut -= zeroIfNull(RETENUE_YO);
        #     resteImpotBrut -= zeroIfNull(RETENUE_YP);
        #     resteImpotBrut -= zeroIfNull(RETENUE_YZ);
        #     resteImpotBrut -= zeroIfNull(RETENUE_WE);
        #     resteImpotBrut -= zeroIfNull(RETENUE_YW);
        #     resteImpotBrut -= zeroIfNull(RETENUE_YQ);
        #     resteImpotBrut -= zeroIfNull(RETENUE_YV);
        #     // YG
        #     double RETENUE_YG = min(zeroIfNull(ins.getYG()), 120000000);
        #     retenue = min(TAUX_50 * RETENUE_YG, 60000000);
        #     double CREDIT_YG = min(retenue, resteImpotBrut);
        #     plaf_credits = plaf_credits - CREDIT_YG;
        #     resteImpotBrut -= CREDIT_YG;
        #     // YX
        #     double RETENUE_YX = ceil(YX * TAUX_80);
        #     RETENUE_YX = min(RETENUE_YX, plaf_credits);
        #     plaf_credits = plaf_credits - RETENUE_YX;
        #     resteImpotBrut -= zeroIfNull(RETENUE_YX);

        #     // Ne pas modifier l'ordre, WX et WS ne sont pas plafonnées, ils sont retenus dans la limite de l'impôt restant
        #     // WX
        #     double RETENUE_WX = min(resteImpotBrut, WX);
        #     resteImpotBrut -= zeroIfNull(RETENUE_WX);
        #     // YS
        #     double RETENUE_YS = min(resteImpotBrut, YS);
        #     resteImpotBrut -= zeroIfNull(RETENUE_YS);

        #     // Stockage des résultats
        #     outs.setPlafondWAWB(plaf_wawb);
        #     outs.setPlafondYOYPYZ(plaf_yoypyz);
        #     outs.setPlafondYV(plaf_yv);
        #     outs.setPlafondCredits(plaf_credits);
        #     outs.setCreditYG(CREDIT_YG);
        #     outs.setReportWB(REPORT_WB);
        #     outs.setReportWE(REPORT_WE);
        #     outs.setReportYO(REPORT_YO);
        #     outs.setReportYQ(REPORT_YQ);
        #     outs.setReportYW(REPORT_YW);
        #     outs.setReportYV(REPORT_YV);
        #     outs.setRetenueWA(RETENUE_WA);
        #     outs.setRetenueWB(RETENUE_WB);
        #     outs.setRetenueWE(RETENUE_WE);

        #     outs.setRetenueYG(RETENUE_YG);
        #     outs.setRetenueYO(RETENUE_YO);
        #     outs.setRetenueYP(RETENUE_YP);
        #     outs.setRetenueYQ(RETENUE_YQ);
        #     outs.setRetenueYV(RETENUE_YV);
        #     outs.setRetenueYW(RETENUE_YW);
        #     outs.setRetenueYX(RETENUE_YX);
        #     outs.setRetenueYZ(RETENUE_YZ);
        #     outs.setRetenueWX(RETENUE_WX);
        #     outs.setRetenueYS(RETENUE_YS);

        #     // Ajout des plus values
        #     resteImpotBrut += zeroIfNull(outs.getPlusValue15());
        #     resteImpotBrut += zeroIfNull(outs.getPlusValue25());
        #     // Ajout des reprises de réductions
        #     resteImpotBrut += zeroIfNull(ins.getYN());

        #     // on le stock aussi là... je sais pas pkoi (cf. drules)
        #     outs.setBaseReduction(resteImpotBrut);
        #     // Impôt net
        #     outs.setDroits(resteImpotBrut);
        # }

        impot_apres_reductions = foyer_fiscal("impot_apres_reductions", period)
        return impot_apres_reductions



import math

def zero_if_null(value):
    """Fonction utilitaire pour remplacer None par 0"""
    return 0 if value is None else value

# Calcul des plafonds
plaf_wawb = math.ceil(TAUX_70 * reste_impot_brut) if (zero_if_null(ins.get_wa()) > 0 or zero_if_null(ins.get_wb()) > 0) else 0
plaf_yoypyz = math.ceil(TAUX_70 * reste_impot_brut) if (zero_if_null(ins.get_yo()) > 0 or zero_if_null(ins.get_yp()) > 0 or zero_if_null(ins.get_yz()) > 0) else 0
plaf_we = math.ceil(TAUX_50 * reste_impot_brut) if zero_if_null(ins.get_we()) > 0 else 0
plaf_yw = math.ceil(TAUX_60 * reste_impot_brut) if zero_if_null(ins.get_yw()) > 0 else 0
plaf_yq = math.ceil(TAUX_50 * reste_impot_brut) if zero_if_null(ins.get_yq()) > 0 else 0
plaf_yv = math.ceil(TAUX_60 * reste_impot_brut) if zero_if_null(ins.get_yv()) > 0 else 0
plaf_yx = reste_impot_brut if YX > 0 else 0
plaf_yg = reste_impot_brut if zero_if_null(ins.get_yg()) > 0 else 0

# L'ensemble des crédits d'impôt ne peut dépasser le plus grand plafond
plaf_credits = max(plaf_wawb, plaf_yoypyz, plaf_we, plaf_yw, plaf_yq, plaf_yv, plaf_yx, plaf_yg)

# WA & WB
temp = zero_if_null(ins.get_wa()) + zero_if_null(ins.get_wb())
retenue = min(temp, plaf_wawb)
retenue = min(retenue, plaf_credits)
den = 1 if temp == 0 else temp

RETENUE_WA = (retenue * zero_if_null(ins.get_wa()) / den) if temp > 0 else 0
RETENUE_WA = math.ceil(RETENUE_WA)

RETENUE_WB = (retenue * zero_if_null(ins.get_wb()) / den) if temp > 0 else 0
RETENUE_WB = math.ceil(RETENUE_WB)

plaf_credits = plaf_credits - RETENUE_WA - RETENUE_WB
plaf_credits = max(plaf_credits, 0)

# On reporte le reste ; WA sur YO
report = temp - plaf_wawb if temp > plaf_wawb else 0
REPORT_YO = (zero_if_null(ins.get_wa()) * report / den) if temp > 0 else 0
REPORT_WB = (zero_if_null(ins.get_wb()) * report / den) if temp > 0 else 0
