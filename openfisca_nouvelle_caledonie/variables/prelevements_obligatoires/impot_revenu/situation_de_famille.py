"""Situation de famille."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal, Individu


class TypesStatutMarital(Enum):
    __order__ = "non_renseigne marie pacse celibataire divorce separe veuf"  # Needed to preserve the enum order in Python 2
    non_renseigne = "Non renseigné"
    marie = "Marié"
    pacse = "Pacsé"
    celibataire = "Célibataire"
    divorce = "Divorcé"
    separe = "Séparé"
    veuf = "Veuf"


class statut_marital(Variable):
    value_type = Enum
    possible_values = TypesStatutMarital
    default_value = TypesStatutMarital.celibataire
    entity = Individu
    label = "Statut marital"
    definition_period = YEAR

    def formula(individu, period):
        # Par défault, on considère que deux adultes dans un foyer fiscal sont PACSÉS
        _ = period
        deux_adultes = individu.foyer_fiscal.nb_persons(FoyerFiscal.DECLARANT) >= 2
        return where(
            deux_adultes, TypesStatutMarital.pacse, TypesStatutMarital.celibataire
        )


class anciens_combattants(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'anciens combattants dans le foyer fiscal"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        _ = period
        return foyer_fiscal.sum(
            foyer_fiscal.members("ancien_combattant", period),
            role=FoyerFiscal.DECLARANT,
        )


class ascendants_a_charge(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Ascendants à charge"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        _ = period
        return foyer_fiscal.nb_persons(role=FoyerFiscal.ASCENDANT_A_CHARGE)


class enfant_en_garde_alternee(Variable):
    value_type = bool
    default_value = False
    entity = Individu
    label = "Enfant en garde alternée"
    definition_period = YEAR


class etudiant_hors_nc(Variable):
    value_type = bool
    default_value = False
    entity = Individu
    label = "Etudiant hors de la Nouvelle Calédonie l'année considérée"
    definition_period = YEAR


class handicape_cejh(Variable):
    value_type = bool
    default_value = False
    entity = Individu
    label = "Handicapé titualaire de la carte CEJH"
    definition_period = YEAR


class taux_invalidite(Variable):
    value_type = float
    default_value = 0
    entity = Individu
    label = "Taux d'invalidité"
    definition_period = YEAR


class ancien_combattant(Variable):
    value_type = bool
    default_value = False
    entity = Individu
    label = "Ancien combattant"
    definition_period = YEAR


class enfants_a_charge_en_nc(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'enfants à charge en NC hors cas particuliers dans le foyer fiscal"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return max_(
            foyer_fiscal.nb_persons(role=FoyerFiscal.ENFANT_A_CHARGE)
            - foyer_fiscal("enfants_handicapes", period)
            - foyer_fiscal("etudiants_hors_nc", period)
            - foyer_fiscal("enfants_en_garde_alternee", period)
            - foyer_fiscal("enfants_en_garde_alternee_handicapes", period),
            0,
        )


class enfants_en_garde_alternee(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'enfants en garde alternée dans le foyer fiscal"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return foyer_fiscal.sum(
            1
            * (
                foyer_fiscal.members("enfant_en_garde_alternee", period)
                * not_(foyer_fiscal.members("handicape_cejh", period))
            ),
            role=FoyerFiscal.ENFANT_A_CHARGE,
        )


class enfants_en_garde_alternee_handicapes(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'enfants en garde alternée handicapés dans le foyer fiscal"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return foyer_fiscal.sum(
            1
            * (
                foyer_fiscal.members("enfant_en_garde_alternee", period)
                * foyer_fiscal.members("handicape_cejh", period)
            ),
            role=FoyerFiscal.ENFANT_A_CHARGE,
        )


class enfants_handicapes(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'enfants handicapés dans le foyer fiscal (hors étudiants hors NC)"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return foyer_fiscal.sum(
            1
            * (
                foyer_fiscal.members("handicape_cejh", period)
                * not_(foyer_fiscal.members("etudiant_hors_nc", period))
                * not_(foyer_fiscal.members("enfant_en_garde_alternee", period))
            ),
            role=FoyerFiscal.ENFANT_A_CHARGE,
        )


class etudiants_hors_nc(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'étudiants hors de la Nouvelle Calédonie l'année considérée"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return foyer_fiscal.sum(
            1 * foyer_fiscal.members("etudiant_hors_nc", period),
            role=FoyerFiscal.ENFANT_A_CHARGE,
        )


class etudiants_hors_nc_ou_enfants_handicapes(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'étudiants hors de la Nouvelle Calédonie ou enfants handicapés"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return foyer_fiscal("etudiants_hors_nc", period) + foyer_fiscal(
            "enfants_handicapes", period
        )


class invalides(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'invalides dans le foyer fiscal"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        _ = period
        return foyer_fiscal.sum(
            foyer_fiscal.members("taux_invalidite", period) > 0.5,
            role=FoyerFiscal.DECLARANT,
        )


class veuf_avec_pac(Variable):
    value_type = bool
    entity = FoyerFiscal
    label = "Veuf avec un enfant à charge"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        _ = period
        statut_marital = foyer_fiscal.declarant_principal("statut_marital", period)
        veuf = statut_marital == TypesStatutMarital.veuf
        nombre_de_pac = foyer_fiscal.nb_persons(
            role=FoyerFiscal.ENFANT_A_CHARGE
        ) + foyer_fiscal.nb_persons(role=FoyerFiscal.ASCENDANT_A_CHARGE)
        return veuf & (nombre_de_pac > 0)


class parts_fiscales(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Nombre de parts"
    definition_period = YEAR

    def formula(foyer_fiscal, period, parameters):
        statut_marital = foyer_fiscal.declarant_principal("statut_marital", period)
        parts_fiscales = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.parts_fiscales

        celibataire_ou_divorce = (
            (statut_marital == TypesStatutMarital.celibataire)
            | (statut_marital == TypesStatutMarital.divorce)
        ) | (statut_marital == TypesStatutMarital.separe)
        marie_ou_pacse = (statut_marital == TypesStatutMarital.marie) | (
            statut_marital == TypesStatutMarital.pacse
        )
        veuf_avec_pac = foyer_fiscal("veuf_avec_pac", period)
        veuf = statut_marital == TypesStatutMarital.veuf
        nombre_de_pac = foyer_fiscal.nb_persons(
            role=FoyerFiscal.ENFANT_A_CHARGE
        ) + foyer_fiscal.nb_persons(role=FoyerFiscal.ASCENDANT_A_CHARGE)

        parts_de_base = select(
            [
                celibataire_ou_divorce | (veuf & (nombre_de_pac == 0)),
                marie_ou_pacse,
                veuf_avec_pac,
            ],
            [
                parts_fiscales.celibataire_divorce_ou_veuf_sans_pac,
                parts_fiscales.marie_ou_pacse,
                parts_fiscales.veuf_avec_pac,
            ],
        )
        parts_additionnelles = parts_fiscales.ancien_combattant * foyer_fiscal(
            "anciens_combattants", period
        ) + parts_fiscales.invalide * foyer_fiscal("invalides", period)

        parts_de_base += parts_additionnelles
        # `enfant` represents whether each member of the foyer fiscal has the role ENFANT_A_CHARGE.
        enfants_en_garde_alternee = foyer_fiscal("enfants_en_garde_alternee", period)
        enfants_en_garde_alternee_handicapes = foyer_fiscal(
            "enfants_en_garde_alternee_handicapes", period
        )

        etudiants_hors_nc_ou_enfants_handicapes = foyer_fiscal(
            "etudiants_hors_nc_ou_enfants_handicapes", period
        )
        parts_enfants = (
            parts_fiscales.enfant_part_entiere * etudiants_hors_nc_ou_enfants_handicapes
            + parts_fiscales.enfant_demi_part
            * (
                0.5 * enfants_en_garde_alternee
                + 1
                * (
                    foyer_fiscal("enfants_a_charge_en_nc", period)
                    + enfants_en_garde_alternee_handicapes
                )
            )
        )
        parts_ascendants = (
            foyer_fiscal("ascendants_a_charge", period)
            * parts_fiscales.ascendant_a_charge
        )

        resident = foyer_fiscal("resident", period)
        return where(
            resident,
            parts_de_base + parts_enfants + parts_ascendants,
            0,
        )


class parts_fiscales_reduites(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Nombre de parts fiscales réduites"
    definition_period = YEAR

    def formula_2015(foyer_fiscal, period, parameters):
        parts_fiscales = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.parts_fiscales
        veuf_avec_pac = foyer_fiscal("veuf_avec_pac", period) * (
            parts_fiscales.veuf_avec_pac - 1
        )
        parts_additionnelles = parts_fiscales.ancien_combattant * foyer_fiscal(
            "anciens_combattants", period
        ) + parts_fiscales.invalide * foyer_fiscal("invalides", period)

        # `enfant` represents whether each member of the foyer fiscal has the role ENFANT_A_CHARGE.
        enfants_en_garde_alternee = foyer_fiscal("enfants_en_garde_alternee", period)
        enfants_en_garde_alternee_handicapes = foyer_fiscal(
            "enfants_en_garde_alternee_handicapes", period
        )

        etudiants_hors_nc_ou_enfants_handicapes = foyer_fiscal(
            "etudiants_hors_nc_ou_enfants_handicapes", period
        )
        parts_enfants = (
            parts_fiscales.enfant_part_entiere * etudiants_hors_nc_ou_enfants_handicapes
            + parts_fiscales.enfant_demi_part
            * (
                0.5 * enfants_en_garde_alternee
                + 1
                * (
                    foyer_fiscal("enfants_a_charge_en_nc", period)
                    + enfants_en_garde_alternee_handicapes
                )
            )
        )
        parts_ascendants = (
            foyer_fiscal("ascendants_a_charge", period)
            * parts_fiscales.ascendant_a_charge
        )

        return (
            foyer_fiscal("parts_fiscales", period)
            - veuf_avec_pac
            - parts_additionnelles
            - parts_enfants
            - parts_ascendants
        )

    # def formula_2015(foyer_fiscal, period, parameters):  TODO: Meilleure formule à conserver
    #     # Réforme de l'impôt 2016 sur les revenus 2015
    #     statut_marital = foyer_fiscal.declarant_principal("statut_marital", period)
    #     parts_fiscales = parameters(
    #         period
    #     ).prelevements_obligatoires.impot_revenu.parts_fiscales
    #     celibataire_ou_divorce = (
    #         (statut_marital == TypesStatutMarital.celibataire)
    #         | (statut_marital == TypesStatutMarital.divorce)
    #     ) | (statut_marital == TypesStatutMarital.separe)
    #     veuf = statut_marital == TypesStatutMarital.veuf
    #     marie_ou_pacse = (statut_marital == TypesStatutMarital.marie) | (
    #         statut_marital == TypesStatutMarital.pacse
    #     )
    #     return select(
    #         [
    #             celibataire_ou_divorce | veuf,
    #             marie_ou_pacse,
    #         ],
    #         [
    #             parts_fiscales.celibataire_divorce_ou_veuf_sans_pac,
    #             parts_fiscales.marie_ou_pacse,
    #         ],
    #     )


class enfants_accueillis(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'enfants accueillis"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        _ = period
        return foyer_fiscal.nb_persons(role=FoyerFiscal.ENFANT_ACCUEILLI)


class enfants_accueillis_handicapes(Variable):
    value_type = int
    default_value = 0
    entity = FoyerFiscal
    label = "Nombre d'enfants accueillis"
    definition_period = YEAR

    def formula(foyer_fiscal, period):
        return foyer_fiscal.sum(
            1 * foyer_fiscal.members("handicape_cejh", period),
            role=FoyerFiscal.ENFANT_ACCUEILLI,
        )
