"""Charges déductibles du revenu global"""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal

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
    cerfa_field = "X0"
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
    value_type = date(2200, 1, 1)
    entity = FoyerFiscal
    label = "Date du prêt souscrit pour votre résidence principale"
    definition_period = YEAR
    cerfa_field = "XP"
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


class deduction_interets_emprunt(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global au titre des intérêts d’emprunt pour votre résidence principale"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        """
        Calcul des charges déductibles du revenu global au titre des intérêts d’emprunt
        pour votre résidence principale
        """

        # Récupération des variables d'intérêts d'emprunt
        interets_emprunt_noumea_etc_recents = foyer_fiscal(
            interets_emprunt_noumea_etc_recents, period
        )
        interets_emprunt_noumea_etc_moins_recents = foyer_fiscal(
            interets_emprunt_noumea_etc_moins_recents, period
        )
        interets_emprunt_hors_noumea_etc_et_anciens = foyer_fiscal(
            interets_emprunt_hors_noumea_etc_et_anciens, period
        )

        # Calcul de la déduction
        # TODO appliquer les palfonds et dates de prêt
        return (
            interets_emprunt_noumea_etc_recents
            + interets_emprunt_noumea_etc_moins_recents
            + interets_emprunt_hors_noumea_etc_et_anciens
        )


class travaux_immobiliers(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Travaux immobiliers effectués par un professionnel dans l'année"
    definition_period = YEAR
    cerfa_field = "XX"


class equipements_verts(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Travaux ou achats d’equipements «verts»"
    definition_period = YEAR
    cerfa_field = "XG"


class deduction_interets_emprunt(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Charges déductibles du revenu global au titre des travaux immobiliers et équipements verts"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        travaux_immobiliers = foyer_fiscal(travaux_immobiliers, period)
        equipements_verts = foyer_fiscal(equipements_verts, period)

        plafond = parameters(period).impot_revenu.charges_deductibles.travaux.plafond
        plafond_travaux_immobiliers
        return max(min_(travaux_immobiliers + equipements_verts, plafond), 0)


class pensions_alimentaires(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Pensions alimentaires versées"
    definition_period = YEAR
    cerfa_field = "XD"


class frais_garde_enfants(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Frais de garde des enfants âgés de moins de 7 ans"
    definition_period = YEAR
    cerfa_field = "XL"


class depenses_internat_transport_interurbain(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Dépenses d’internat et de transport interurbain pour enfants scolarisés"
    definition_period = YEAR
    cerfa_field = "XZ"


class services_a_la_personne(Variable):
    unit = "currency"
    value_type = float
    entity = FoyerFiscal
    label = "Service à la personne"
    definition_period = YEAR
    cerfa_field = "XK"
