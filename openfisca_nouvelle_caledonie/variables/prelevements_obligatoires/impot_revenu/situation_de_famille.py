"""Situation de famille."""

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import FoyerFiscal, Person as Individu


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
        veuf = statut_marital == TypesStatutMarital.veuf
        marie_ou_pacse = (statut_marital == TypesStatutMarital.marie) | (
            statut_marital == TypesStatutMarital.pacse
        )
        nombre_de_pac = foyer_fiscal.nb_persons(
            role=FoyerFiscal.ENFANT_A_CHARGE
        ) + foyer_fiscal.nb_persons(role=FoyerFiscal.ASCENDANT_A_CHARGE)
        parts_de_base = select(
            [
                celibataire_ou_divorce | (veuf & (nombre_de_pac == 0)),
                marie_ou_pacse,
                veuf & (nombre_de_pac > 0),
            ],
            [
                parts_fiscales.celibataire_divorce_ou_veuf_sans_pac,
                parts_fiscales.marie_ou_pacse,
                parts_fiscales.veuf_avec_pac,
            ],
        )
        parts_additionnelles = parts_fiscales.ancien_combattant * (
            foyer_fiscal.declarant_principal("ancien_combattant", period)
        ) + parts_fiscales.handicape * (
            1
            * (
                foyer_fiscal.declarant_principal("taux_invalidite", period) > 0.5
            )  # TODO: parameters
            + 1
            * (
                foyer_fiscal.conjoint("taux_invalidite", period) > 0.5
            )  # TODO: parameters
        )
        parts_de_base += parts_additionnelles
        # `enfant` represents whether each member of the fiscal household has the role ENFANT_A_CHARGE.
        enfant = foyer_fiscal.members.has_role(FoyerFiscal.ENFANT_A_CHARGE)
        enfant_en_garde_alternee_i = enfant * foyer_fiscal.members(
            "enfant_en_garde_alternee", period
        )
        etudiant_hors_nc_i = enfant * foyer_fiscal.members("etudiant_hors_nc", period)
        handicape_cejh_i = enfant * foyer_fiscal.members("handicape_cejh", period)
        invalidite_i = enfant * (foyer_fiscal.members("taux_invalidite", period) > 0.5)

        enfants_parts_entiere_i = (etudiant_hors_nc_i + handicape_cejh_i + invalidite_i)
        parts_enfants = (
            foyer_fiscal.sum(  # TODO: Erreur dans le calcul des parts garde alternée
                (
                    parts_fiscales.enfant_part_entiere
                    * (enfants_parts_entiere_i)
                    * (
                        1 * not_(enfant_en_garde_alternee_i)
                        + 0.5 * enfant_en_garde_alternee_i
                    )
                    + parts_fiscales.enfant_demi_part
                    * not_(enfants_parts_entiere_i)
                    * (
                        1 * not_(enfant_en_garde_alternee_i)
                        + 0.5 * enfant_en_garde_alternee_i
                    )
                ),
                role=FoyerFiscal.ENFANT_A_CHARGE,
            )
        )
        parts_ascendants = (
            foyer_fiscal.nb_persons(role=FoyerFiscal.ASCENDANT_A_CHARGE)
            * parts_fiscales.ascendant_a_charge
        )

        return parts_de_base + parts_enfants + parts_ascendants


class parts_fiscales_reduites(Variable):
    value_type = float
    entity = FoyerFiscal
    label = "Nombre de parts"
    definition_period = YEAR

    def formula_2015(foyer_fiscal, period, parameters):
        # Réforme de l'impôt 2016 sur les revenus 2015
        statut_marital = foyer_fiscal.declarant_principal("statut_marital", period)
        parts_fiscales = parameters(
            period
        ).prelevements_obligatoires.impot_revenu.parts_fiscales
        celibataire_ou_divorce = (
            (statut_marital == TypesStatutMarital.celibataire)
            | (statut_marital == TypesStatutMarital.divorce)
        ) | (statut_marital == TypesStatutMarital.separe)
        veuf = statut_marital == TypesStatutMarital.veuf
        marie_ou_pacse = (statut_marital == TypesStatutMarital.marie) | (
            statut_marital == TypesStatutMarital.pacse
        )
        return select(
            [
                celibataire_ou_divorce | veuf,
                marie_ou_pacse,
            ],
            [
                parts_fiscales.celibataire_divorce_ou_veuf_sans_pac,
                parts_fiscales.marie_ou_pacse,
            ],
        )


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
