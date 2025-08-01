"""Charges déductibles du revenu global."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal


class charges_deductibles(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        # TODO: vérifier si la formule est correcte
        return (
            foyer_fiscal("ccs_deductible", period)
            + foyer_fiscal("deduction_depenses_internat_transport_interurbain", period)
            + foyer_fiscal("deduction_frais_garde_enfants", period)
            + foyer_fiscal("deduction_immeubles_historiques", period)
            + foyer_fiscal("deduction_interets_emprunt", period)
            + foyer_fiscal("deduction_primes_assurance_vie", period)
            + foyer_fiscal("deduction_services_a_la_personne", period)
            + foyer_fiscal("deduction_travaux_immobiliers_equipements_verts", period)
            + foyer_fiscal("deduction_travaux_immobiliers", period)
            + foyer_fiscal("deduction_pensions_alimentaires", period)
            + foyer_fiscal("retenue_cotisations_sociales", period)
        )


# INTÉRÊTS D’EMPRUNT POUR VOTRE RÉSIDENCE PRINCIPALE
# EN NOUVELLE-CALÉDONIE (lignes XI, XO, XP)
# Vous pouvez bénéficier d’une déduction au titre des intérêts d’emprunts contractés
# pour acquérir ou construire votre résidence principale y compris l’assiette foncière
# dans la limite de 10 ares ou financer des travaux dans celle-ci (agrandissements,
# construction, grosses réparations). La date de conclusion du contrat s’entend de
# celle de votre acceptation de l’offre de prêt. Inscrivez dans la case correspondant à
# la situation du bien et à la date du prêt le total intérêts + assurance décès versés
# en 2024.


class interets_emprunt_noumea_etc_recents(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Intérêts d’emprunt pour votre résidence principale à Nouméa, Dumbéa, Païta ou Mont-Dore souscrit entre 2019-2021"
    definition_period = YEAR
    cerfa_field = "XI"


class interets_emprunt_noumea_etc_moins_recents(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Intérêts d’emprunt pour votre résidence principale à Nouméa (souscrit à partir de 2004), Dumbéa, Païta ou Mont-Dore (souscrit à partir de 2017)"
    definition_period = YEAR
    cerfa_field = "XO"
    # TODO: VEFA ? Condiiton XI


class interets_emprunt_hors_noumea_etc_et_anciens(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Intérêts d’emprunt pour votre résidence principale à Nouméa (souscrit à partir de 2004), Dumbéa, Païta ou Mont-Dore (souscrit à partir de 2017)"
    definition_period = YEAR
    cerfa_field = "XP"
    # TODO: VEFA ? Condiiton XI


class interets_emprunt_date_du_pret(Variable):
    unit = "currency"
    value_type = date
    default_value = date(2200, 1, 1)
    entity = FoyerFiscal
    label = "Date du prêt souscrit pour votre résidence principale"
    definition_period = YEAR
    # TODO: VEFA ? Condiiton XI


# IMPORTANT :
# - Pour les immeubles situés à Nouméa : la déduction est admise dans la limite de
# 500 000 F et pour les 20 premières annuités de remboursement (limite relevée à 1
# million F sous certaines conditions, voir ci-dessous).
# - Pour les immeubles situés hors des communes de Nouméa, Dumbéa, Païta, Mont-
# Dore quelle que soit la date du prêt et à Dumbéa, païta, Mont-Dore si le prêt a été
# contracté avant le 01/01/2017 : la déduction n’est pas limitée.
# - Pour les immeubles situés à Dumbéa, Païta et Mont-Dore si le prêt a été contracté
# à compter du 01/01/2017: la déduction est plafonnée à 500 000 F CFP pour les
# 20 premières annuités (limite relevée à 1 million F sous certaines conditions, voir
# ci-dessous).
# - Pour les immeubles que vous avez fait construire ou que vous avez acquis en VEFA
# sur Nouméa, Dumbéa, Païta et Mont-Dore avec un prêt contracté en 2019, 2020
# et 2021, la déduction est plafonnée à 1 000 000 F CFP pour les 20 premières
# annuités.


class interets_emprunt_noumea_etc_anciens(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Intérêts d’emprunt pour une résidence à Nouméa (souscrit en 1997 ou 1998) quelle que soit l'objet' du prêt"
    definition_period = YEAR
    cerfa_field = "XV"


class interets_emprunt_residence_secondaire_anciens(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = (
        "Intérêts d’emprunt pour votre résidence secondaire (souscrit en 1997 ou 1998)"
    )
    definition_period = YEAR
    cerfa_field = "XW"


class deduction_interets_emprunt(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global au titre des intérêts d’emprunt pour votre résidence principale"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        interets_emprunt = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.charges_deductibles.interets_emprunt
        # Récupération des variables d'intérêts d'emprunt
        interets_emprunt_noumea_etc_recents = max_(
            min_(
                foyer_fiscal("interets_emprunt_noumea_etc_recents", period),
                interets_emprunt.noumea_etc_recents,
            ),
            0,
        )
        interets_emprunt_noumea_etc_moins_recents = max_(
            min_(
                foyer_fiscal("interets_emprunt_noumea_etc_moins_recents", period),
                interets_emprunt.noumea_etc_moins_recents,
            ),
            0,
        )
        interets_emprunt_hors_noumea_etc_et_anciens = foyer_fiscal(
            "interets_emprunt_hors_noumea_etc_et_anciens", period
        )

        autres = foyer_fiscal(
            "interets_emprunt_noumea_etc_anciens", period
        ) + foyer_fiscal("interets_emprunt_residence_secondaire_anciens", period)
        return (
            interets_emprunt_noumea_etc_recents
            + interets_emprunt_noumea_etc_moins_recents
            + interets_emprunt_hors_noumea_etc_et_anciens
            + autres
        )


class travaux_immobiliers(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Travaux immobiliers effectués par un professionnel dans l'année"
    definition_period = YEAR
    cerfa_field = "XX"


class deduction_travaux_immobiliers(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global au titre des travaux immobiliers"
    definition_period = YEAR
    end = "2011-12-31"

    def formula_2008(foyer_fiscal, period, parameters):
        # TODO: vérifier si la date de fin est correcte et corriger avec deduction_travaux_immobiliers_equipements_verts
        travaux_immobiliers = foyer_fiscal("travaux_immobiliers", period)
        plafond = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.charges_deductibles.travaux_immobiliers
        return max_(min_(travaux_immobiliers, plafond), 0)


class equipements_verts(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Travaux ou achats d’equipements «verts»"
    definition_period = YEAR
    cerfa_field = "XG"


class deduction_travaux_immobiliers_equipements_verts(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global au titre des travaux immobiliers et équipements verts"
    definition_period = YEAR

    def formula_2023(foyer_fiscal, period, parameters):
        travaux_immobiliers = foyer_fiscal("travaux_immobiliers", period)
        equipements_verts = foyer_fiscal("equipements_verts", period)

        plafond = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.charges_deductibles.travaux
        return max_(min_(travaux_immobiliers + equipements_verts, plafond), 0)


class pensions_alimentaires(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Pensions alimentaires versées"
    definition_period = YEAR
    cerfa_field = "XD"


class deduction_pensions_alimentaires(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Pensions alimentaires retenues"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return where(
            foyer_fiscal("resident", period),
            foyer_fiscal("pensions_alimentaires", period),
            0,
        )


class frais_garde_enfants(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Frais de garde des enfants âgés de moins de 7 ans"
    definition_period = YEAR
    cerfa_field = "XL"


class deduction_frais_garde_enfants(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global au titre des frais de garde d’enfants"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        plafond = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.charges_deductibles.frais_garde_enfants
        resident = foyer_fiscal("resident", period)
        return where(
            resident,
            max_(
                min_(
                    foyer_fiscal("frais_garde_enfants", period),
                    plafond,
                ),
                0,
            ),
            0,
        )


class depenses_internat_transport_interurbain(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Dépenses d’internat et de transport interurbain pour enfants scolarisés"
    definition_period = YEAR
    cerfa_field = "XZ"


class deduction_depenses_internat_transport_interurbain(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global au titre des dépenses d’internat et de transport interurbain pour enfants scolarisés"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        plafond = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.charges_deductibles.depenses_internat_transport_interurbain
        resident = foyer_fiscal("resident", period)
        return where(
            resident,
            max_(
                min_(
                    foyer_fiscal("depenses_internat_transport_interurbain", period),
                    plafond,
                ),
                0,
            ),
            0,
        )


class services_a_la_personne(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Service à la personne"
    definition_period = YEAR
    cerfa_field = "XK"


class deduction_services_a_la_personne(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global au titre des services à la personne"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        plafond = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.charges_deductibles.services_a_la_personne
        return max_(min_(foyer_fiscal("services_a_la_personne", period), plafond), 0)


class cotisations_sociales_hors_gerant_societes_retraite_avant_1992(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Cotisations sociales hors gérant de sociétés pour les contrats de retraite volontaires souscrits avant 1992"
    definition_period = YEAR
    cerfa_field = "XE"


class cotisations_sociales_hors_gerant_societes_retraite_apres_1992(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Cotisations sociales hors gérant de sociétés pour les contrats de retraite volontaires souscrits après 1992"
    definition_period = YEAR
    cerfa_field = "XT"


class cotisations_sociales_hors_gerant_societes_autres(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = (
        "Cotisations sociales hors gérant de sociétés : autres cotisations volontaires"
    )
    definition_period = YEAR
    cerfa_field = "XY"


class retenue_cotisations_sociales(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Retenue pour cotisations sociales"
    definition_period = YEAR

    def formula_2013(foyer_fiscal, period, parameters):
        resident = foyer_fiscal("resident", period)
        period_plafond = period.start.offset("first-of", "month").offset(11, "month")
        plafond_cafat_retraite = parameters(
            period_plafond
        ).prelevements_obligatoires.prelevements_sociaux.cafat.maladie_retraite.plafond_retraite_mensuel
        return where(
            resident,
            (
                min_(
                    (
                        foyer_fiscal(
                            "cotisations_sociales_hors_gerant_societes_retraite_avant_1992",
                            period,
                        )
                        + foyer_fiscal(
                            "cotisations_sociales_hors_gerant_societes_retraite_apres_1992",
                            period,
                        )
                    ),
                    7 * plafond_cafat_retraite,
                )
                + foyer_fiscal(
                    "cotisations_sociales_hors_gerant_societes_autres", period
                )
            ),
            0,
        )


class primes_assurance_vie(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Primes d’assurance vie"
    definition_period = YEAR
    cerfa_field = "XF"


class deduction_primes_assurance_vie(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global au titre des primes d’assurance vie"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        plafond = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.charges_deductibles.assurance_vie
        return where(
            foyer_fiscal("resident", period),
            max_(min_(foyer_fiscal("primes_assurance_vie", period), plafond), 0),
            0,
        )


class ccs_deductible(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "CSG déductible"
    definition_period = YEAR
    cerfa_field = "XC"


class immeubles_historiques(Variable):
    unit = "currency"
    value_type = float
    cerfa_field = "XS"
    entity = FoyerFiscal
    label = "Dépenses pour immeubles historiques."
    definition_period = YEAR


class deduction_immeubles_historiques(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Réduction d'impôt immeubles historiques."
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        plafond = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.charges_deductibles.immeubles_historiques
        return max_(min_(foyer_fiscal("immeubles_historiques", period), plafond), 0)


class deductions_reintegrees(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    cerfa_field = "YM"
    label = "Deductions réintégrées"
    definition_period = YEAR
