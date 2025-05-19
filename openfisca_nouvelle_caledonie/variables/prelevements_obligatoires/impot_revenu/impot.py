"""Calcul de l'impôt sur le revenu."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal


class revenu_brut_global(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Revenu brut global"
    definition_period = YEAR

    def formula(foyer_fiscal, period):

        revenus_categoriels_tspr = foyer_fiscal("revenus_categoriels_tspr", period)


    #     // benefice
    #     rbg += zeroIfNegative(outs.getBeneficeBicP());
    #     rbg += zeroIfNegative(outs.getBeneficeBicC());
    #     rbg += zeroIfNegative(outs.getBeneficeBicPC());
    #     rbg += zeroIfNegative(outs.getBeneficeBaP());
    #     rbg += zeroIfNegative(outs.getBeneficeBaC());
    #     rbg += zeroIfNegative(outs.getBeneficeBaPC());
    #     rbg += zeroIfNegative(outs.getBeneficeBncP());
    #     rbg += zeroIfNegative(outs.getBeneficeBncC());
    #     rbg += zeroIfNegative(outs.getBeneficeBncPC());

    #     // pension
    #     rbg += zeroIfNull(outs.getPensionP());
    #     rbg += zeroIfNull(outs.getPensionC());
    #     rbg += zeroIfNull(outs.getPensionPC());

    #     // "REVENUS_FONCIERS" est egal a "AA"
    #     // "REVENU_BRUT_GLOBAL" est egal a "REVENU_BRUT_GLOBAL + REVENUS_FONCIERS"
    #     rbg += zeroIfNull(ins.getAA());

    #     rbg += zeroIfNull(outs.getCapitauxMobiliers());

    #     outs.setRevenuBrutGlobal(rbg);
    # }


        # revenus_categoriels_capital = foyer_fiscal("revenu_categoriel_capital", period)
        # revenus_categoriels_foncier = foyer_fiscal("revenu_categoriel_foncier", period)
        # revenus_categoriels_non_salarie = foyer_fiscal("revenu_categoriel_non_salarie", period)
        # revenus_categoriels_plus_values = foyer_fiscal("revenu_categoriel_plus_values", period)

        return (
            revenus_categoriels_tspr
            # + revenu_categoriel_capital
            # + revenu_categoriel_foncier
            # + revenu_categoriel_non_salarial
            # + revenu_categoriel_plus_values
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
            0
            )


class revenu_net_global_imposable(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Revenu net global imposable"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return foyer_fiscal("revenu_brut_global", period) - foyer_fiscal("charges_deductibles", period)


class impot_brut(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Impot brut"
    definition_period = YEAR


    def formula(foyer_fiscal, period, parameters):
        # from tmp/engine/rules/_2008/impots/ImpotBrutUtil2008.java
        tauxPart1 = 8 / 100

        taux_moyen_imposition_non_resident = foyer_fiscal("taux_moyen_imposition_non_resident", period)

        # Calcul de l'impôt brut pour les résidents

        nombre_de_parts = foyer_fiscal("parts_fiscales", period)
        # double rni = zeroIfNull(outs.getRevenuNonImposable());
        revenu_non_imposable = foyer_fiscal("revenu_non_imposable", period)
        revenu_net_global_imposable = foyer_fiscal("revenu_net_global_imposable", period)

        revenu_par_part = (
            max_(revenu_net_global_imposable, 0)
            + revenu_non_imposable
            ) / nombre_de_parts

        bareme = parameters(period).prelevements_obligatoires.impot_revenu.bareme

        impot_brut = bareme.calc(revenu_par_part)

        # Au final, l'impôt brut est une fraction du résultat précédent
        numerateur = revenu_net_global_imposable
        denominateur = where(
            numerateur > 0,
            numerateur + revenu_non_imposable,
            1
            )
        fraction = where(
            numerateur > 0,
            numerateur / denominateur,
            1
            )

        impot_brut = where(
            impot_brut > 0,
            impot_brut,
            0
            )
        impot_brut = where(
            fraction < 0.01,  # TODO: à introduire dans les paramètres
            0,
            impot_brut * fraction
            )

        # L'impôt brut est plafonné à 50% des revenus
        taux_plafond = parameters(period).prelevements_obligatoires.impot_revenu.taux_plafond
        impot_brut_resident = min_(taux_plafond * revenu_net_global_imposable, impot_brut)

        # TODO: à inclure ailleurs
        # if (zeroIfNull(rngi) != 0) {
        #     outs.setTauxImpot(impotBrut / rngi);
        # }

        # Calcul de l'impôt brut Non résident
        revenu_brut_global = foyer_fiscal("revenu_brut_global", period)
        den = where(
            revenu_brut_global == 0,
            1,
            revenu_brut_global,
            )
        interets_de_depots = foyer_fiscal("interets_de_depots", period)
        pourcentage = where(
            revenu_brut_global == 0,
            0,
            interets_de_depots,  # case BB
            ) / den
        # //  TxNI= 25 % si case 46 = 1 et case 47 =vide
        txNI = where(
            taux_moyen_imposition_non_resident > 0,
            taux_moyen_imposition_non_resident,
            0.25
            )

        # // 8% x RNGI x pourcentage
        part1 = tauxPart1 * revenu_net_global_imposable * pourcentage;		# // txNI x rngi x (1 - pourcentage)
        part2 = txNI * revenu_net_global_imposable * (1 - pourcentage);

        # Résultat pour les non résidents
        impot_brut_non_resident = part1 + part2;

        # if (zeroIfNull(rngi) != 0) {
        # 	outs.setTauxImpot(impotBrut / rngi);
        # } TODO: à inclure ailleurs

        return where(
            foyer_fiscal("resident", period),
            impot_brut_resident,
            impot_brut_non_resident,
            )

#     /**
#      * Permet de recalculer l'impôt supplémentaire dû à un salaire différé ou à une pension différée. Il se base sur la calcul de l'impôt brut
#      *
#      * @param quotient
#      * @param nbAnnee
#      * @param ins
#      * @param outs
#      * @return le montant de l'impôt supplémentaire
#      */
#     static Double calculImpotSupplementaireQuotientDiff(Double quotient, Double nbAnnee, CalculInputs ins, CalculOutputs outs) {
#         if (quotient != null) {
#             double rngiRevise = arrondit1000(outs.getRevenuNetGlobalImposable() + quotient);
#             double impotBrutRevise = ImpotBrutUtil2008.calculImpotBrut(rngiRevise, ins, outs);
#             return (impotBrutRevise - outs.getImpotBrut()) * nbAnnee;
#         }
#         return null;
#     }
# }


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
