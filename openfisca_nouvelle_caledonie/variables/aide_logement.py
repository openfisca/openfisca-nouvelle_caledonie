"""Variables pour le calcul des aides au logement."""

from openfisca_core.indexed_enums import Enum
from openfisca_core.model_api import max_, min_, select, where
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable
from openfisca_nouvelle_caledonie.entities import Menage


class TypologieLogement(Enum):
    __order__ = "chambre f1 f2 f3 f4 f5p maisonderetraite"
    chambre = "Chambre"
    f1 = "F1"
    f2 = "F2"
    f3 = "F3"
    f4 = "F4"
    f5p = "F5 et suivants"
    maisonderetraite = "Maison de retraite"


class typologie_logement(Variable):
    value_type = Enum
    possible_values = TypologieLogement
    default_value = TypologieLogement.chambre
    entity = Menage
    definition_period = MONTH
    label = "Legal housing situation of the menage concerning their main residence"


class loyer(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Loyer de base hors charges"


class charges_locatives(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Charges locatives"


class aide_logement_loyer(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Loyer mensuel de base"

    def formula(menage, period):
        loyer_mensuel_reference = menage("loyer_mensuel_reference", period)
        loyer = menage("loyer", period)

        typologie_logement = menage("typologie_logement", period)

        # Clarification nécessaire
        # Prise en compte ou non de l'excédent de loyer pour charges importantes ?
        return where(
            typologie_logement == TypologieLogement.maisonderetraite,
            loyer_mensuel_reference,
            min_(loyer, loyer_mensuel_reference),
        )


class loyer_mensuel_reference(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Loyer mensuel de référence"

    def formula(menage, period, parameters):
        typologie_logement = menage("typologie_logement", period)
        return parameters(period).benefits.aide_logement.loyer_mensuel_reference[
            typologie_logement
        ]


class loyer_mensuel_plafond(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Loyer mensuel de référence"

    def formula(menage, period, parameters):
        loyer_mensuel_reference = menage("loyer_mensuel_reference", period)
        params = parameters(period).benefits.aide_logement.loyer_mensuel_plafond
        pourcentage_plafond = params.pourcentage
        excedent_pour_charges = params.excedent_pour_charges

        charges = menage("charges_locatives", period)
        excedent_pour_charges_montant = max_(
            0, charges - loyer_mensuel_reference * excedent_pour_charges
        )

        # Clarification nécessaire
        # return loyer_mensuel_reference * (1 + pourcentage_plafond) + excedent_pour_charges_montant
        # OU
        # return (loyer_mensuel_reference + excedent_pour_charges_montant) * (1 + pourcentage_plafond)
        return (loyer_mensuel_reference + excedent_pour_charges_montant) * (
            1 + pourcentage_plafond
        )


class famille_monoparentale(Variable):
    value_type = bool
    entity = Menage
    definition_period = MONTH

    def formula(menage, period):
        return (menage("aide_logement_nb_adultes", period) == 1) * (
            menage("aide_logement_nb_enfants", period) > 0
        )


class aide_logement_nb_adultes(Variable):
    value_type = int
    default_value = 1
    entity = Menage
    definition_period = MONTH


class aide_logement_nb_enfants(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH


class aide_logement_forfait_familial(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Solde de revenu pour le calcul de l'aide au logement"

    def formula(menage, period, parameters):
        monoparentale = menage("famille_monoparentale", period)
        nb_adultes = menage("aide_logement_nb_adultes", period)
        nb_enfants = menage("aide_logement_nb_enfants", period)

        forfait_familial = parameters(period).benefits.aide_logement.forfait_familial
        forfait_individuel = forfait_familial.forfait_individuel

        coef_base = forfait_familial.coefficient
        coef_monoparentale = forfait_familial.coefficient_monoparentale
        coef_adulte = forfait_familial.coefficient_adulte
        coef_enfant = forfait_familial.coefficient_enfant

        coef = where(monoparentale, coef_monoparentale, coef_base)

        return forfait_individuel * (
            coef + coef_adulte * (nb_adultes - 1) + coef_enfant * nb_enfants
        )


class aide_logement_solde_revenu(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Solde de revenu pour le calcul de l'aide au logement"

    def formula(menage, period):
        base_ressources = menage("aide_logement_base_ressources", period)
        forfait_familial = menage("aide_logement_forfait_familial", period)

        return base_ressources - forfait_familial


class aide_logement_supplement_loyer_sr_negatif(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Supplément de loyer pour le calcul de l'aide au logement"

    def formula(menage, period, parameters):
        # Clarification nécessaire
        loyer_base = menage("aide_logement_loyer", period)
        loyer_reference = menage("loyer_mensuel_reference", period)
        retraite = menage("aide_logement_cas_particulier_retraite", period)
        loyer = where(retraite, loyer_reference, loyer_base)
        aide_logement_neutralisation_loyer = menage(
            "aide_logement_neutralisation_loyer", period
        )

        charges = menage("charges_locatives", period)

        typologie = menage("typologie_logement", period)
        p = parameters(
            period
        ).benefits.aide_logement.supplement_loyer.solde_revenu_negatif_pourcentage[
            typologie
        ]

        a = (
            loyer * (1 - aide_logement_neutralisation_loyer)
            + charges
            - loyer_reference * (1 - aide_logement_neutralisation_loyer)
        )
        b = p * loyer_reference
        return min_(a, b)


class aide_logement_supplement_loyer_sr_bas_positif(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Supplément de loyer pour le calcul de l'aide au logement"

    def formula(menage, period, parameters):
        # Clarification nécessaire
        loyer_base = menage("aide_logement_loyer", period)
        loyer_reference = menage("loyer_mensuel_reference", period)
        retraite = menage("aide_logement_cas_particulier_retraite", period)
        loyer = where(retraite, loyer_reference, loyer_base)

        charges = menage("charges_locatives", period)
        loyer_reference = menage("loyer_mensuel_reference", period)
        aide_logement_neutralisation_loyer = menage(
            "aide_logement_neutralisation_loyer", period
        )

        typologie = menage("typologie_logement", period)

        pa = parameters(
            period
        ).benefits.aide_logement.supplement_loyer.solde_revenu_positif_pourcentage_charges
        a = pa * (
            loyer * (1 - aide_logement_neutralisation_loyer)
            + charges
            - loyer_reference * (1 - aide_logement_neutralisation_loyer)
        )

        pb = parameters(
            period
        ).benefits.aide_logement.supplement_loyer.solde_revenu_positif_pourcentage[
            typologie
        ]
        b = pb * loyer_reference
        return min_(a, b)


class aide_logement_supplement_loyer(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Supplément de loyer pour le calcul de l'aide au logement"

    def formula(menage, period, parameters):
        solde_revenu = menage("aide_logement_solde_revenu", period)
        loyer_reference = menage("loyer_mensuel_reference", period)

        negatif = menage("aide_logement_supplement_loyer_sr_negatif", period)
        faible = menage("aide_logement_supplement_loyer_sr_bas_positif", period)

        plafond_sr = parameters(
            period
        ).benefits.aide_logement.supplement_loyer.pourcentage_plafond_solde_revenu

        return select(
            [solde_revenu <= 0, solde_revenu <= plafond_sr * loyer_reference],
            [negatif, faible],
            default=0,
        )


class aide_sociale(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Base ressources pour le calcul de l'aide au logement"


class bourse(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Base ressources pour le calcul de l'aide au logement"


class salaire(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Base ressources pour le calcul de l'aide au logement"


class retraite(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Base ressources pour le calcul de l'aide au logement"


class pension_recue(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Base ressources pour le calcul de l'aide au logement"


class pension_versee(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Base ressources pour le calcul de l'aide au logement"


class autres_revenus(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Base ressources pour le calcul de l'aide au logement"


class aide_sociale_et_bourse(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Base ressources pour le calcul de l'aide au logement"

    def formula(menage, period, parameters):
        aide_sociale = menage("aide_sociale", period)
        bourse = menage("bourse", period)
        franchise_aides_et_bourses = parameters(
            period
        ).benefits.aide_logement.base_ressources.franchise_aides_et_bourses
        return max_(0, aide_sociale - franchise_aides_et_bourses) + max_(
            0, bourse - franchise_aides_et_bourses
        )


class aide_logement_base_ressources(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Base ressources pour le calcul de l'aide au logement"

    def formula(menage, period):
        return (
            menage("aide_sociale_et_bourse", period)
            + menage("salaire", period)
            + menage("retraite", period)
            + menage("pension_recue", period)
            - menage("pension_versee", period)
            + menage("autres_revenus", period)
        )


class aide_logement_contribution_locataire_sr_negatif(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Contribution du locataire pour le calcul de l'aide au logement"

    def formula(menage, period, parameters):
        base_ressources = menage("aide_logement_base_ressources", period)

        contribution_locataire = parameters(
            period
        ).benefits.aide_logement.contribution_locataire
        minimum = contribution_locataire.montant_minimum
        minimum_aides_bourses = contribution_locataire.montant_minimum_aides_bourses

        aide_sociale = menage("aide_sociale", period)
        bourse = menage("bourse", period)
        aides_sociales_et_bourses = aide_sociale + bourse

        pourcentage_ressources = contribution_locataire.pourcentage_ressources
        return max_(
            where(aides_sociales_et_bourses > 0, minimum_aides_bourses, minimum),
            pourcentage_ressources * base_ressources,
        )


class aide_logement_nb_personnes(Variable):
    value_type = int
    entity = Menage
    definition_period = MONTH

    def formula(menage, period):
        return menage("aide_logement_nb_adultes", period) + menage(
            "aide_logement_nb_enfants", period
        )


class aide_logement_plafond_contribution(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH

    def formula(menage, period, parameters):
        nb_personnes = menage("aide_logement_nb_personnes", period)
        base_ressources = menage("aide_logement_base_ressources", period)

        contribution_locataire = parameters(
            period
        ).benefits.aide_logement.contribution_locataire
        pourcentage_plafond = (
            contribution_locataire.plafond.pourcentage_ressources.calc(nb_personnes)
        )

        return pourcentage_plafond * base_ressources


class personne_retraitee(Variable):
    value_type = bool
    entity = Menage
    definition_period = MONTH


# Clarification nécessaire
class aide_logement_coef_error(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    default_value = 1


# Clarification nécessaire
class aide_logement_neutralisation_loyer(Variable):
    value_type = bool
    entity = Menage
    definition_period = MONTH


class aide_logement_cas_particulier_retraite(Variable):
    value_type = bool
    entity = Menage
    definition_period = MONTH

    def formula(menage, period):
        ret = menage("personne_retraitee", period)
        base_ressources = menage("aide_logement_base_ressources", period)
        nb_adultes = menage("aide_logement_nb_adultes", period)
        nb_enfs = menage("aide_logement_nb_enfants", period)

        c1 = (nb_adultes == 1) * (nb_enfs == 0) * (base_ressources <= 90000)
        c2 = (nb_adultes > 1) * (base_ressources <= 110000)
        c3 = (nb_enfs > 0) * (base_ressources <= 110000)

        return ret * (c1 + c2 + c3)


class aide_logement_contribution_minimale_montant_base(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH

    def formula(menage, period, parameters):
        base_ressources = menage("aide_logement_base_ressources", period)
        solde_revenu = menage("aide_logement_solde_revenu", period)

        contribution_locataire = parameters(
            period
        ).benefits.aide_logement.contribution_locataire
        pourcentage_ressources = contribution_locataire.pourcentage_ressources

        return pourcentage_ressources * base_ressources + solde_revenu * menage(
            "aide_logement_coef_error", period
        )


class aide_logement_contribution_minimale_montant_retraite(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH

    def formula(menage, period, parameters):
        base_ressources = menage("aide_logement_base_ressources", period)
        plafond = parameters(
            period
        ).benefits.aide_logement.base_ressources.franchise_aides_et_bourses

        contribution_locataire = parameters(
            period
        ).benefits.aide_logement.contribution_locataire
        minimum = contribution_locataire.montant_minimum
        minimum_aides_bourses = contribution_locataire.montant_minimum_aides_bourses

        aide_sociale = menage("aide_sociale", period)
        bourse = menage("bourse", period)
        aides_sociales_et_bourses = aide_sociale + bourse

        return (
            where(aides_sociales_et_bourses > 0, minimum_aides_bourses, minimum)
            + max_(0, base_ressources - plafond) / 3.0
        )


class aide_logement_contribution_minimale(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH

    def formula(menage, period):
        montant_base = menage(
            "aide_logement_contribution_minimale_montant_base", period
        )
        montant_retraite = menage(
            "aide_logement_contribution_minimale_montant_retraite", period
        )
        retraite = menage("aide_logement_cas_particulier_retraite", period)

        return where(retraite, min_(montant_retraite, montant_base), montant_base)


class aide_logement_contribution_locataire_sr_positif(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Contribution du locataire pour le calcul de l'aide au logement"

    def formula(menage, period):
        clm = menage("aide_logement_contribution_minimale", period)
        pc = menage("aide_logement_plafond_contribution", period)
        return min_(clm, pc)


class aide_logement_contribution_locataire(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Contribution du locataire pour le calcul de l'aide au logement"

    def formula(menage, period):
        solde_revenu = menage("aide_logement_solde_revenu", period)

        negatif = menage("aide_logement_contribution_locataire_sr_negatif", period)
        positif = menage("aide_logement_contribution_locataire_sr_positif", period)

        return select([solde_revenu <= 0], [negatif], default=positif)


class aide_logement_montant(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Aide au logement"

    def formula(menage, period, parameters):
        seuil_paiement = parameters(period).benefits.aide_logement.seuil_paiement

        loyer = menage("aide_logement_loyer", period)
        supplement_loyer = menage("aide_logement_supplement_loyer", period)
        contribution = menage("aide_logement_contribution_locataire", period)
        montant = loyer + supplement_loyer - contribution

        return (montant >= seuil_paiement) * montant


class aide_logement(Variable):
    value_type = float
    entity = Menage
    definition_period = MONTH
    label = "Aide au logement"

    def formula(menage, period):
        montant = menage("aide_logement_montant", period)
        loyer = menage("loyer", period)
        loyer_mensuel_plafond = menage("loyer_mensuel_plafond", period)

        typologie_logement = menage("typologie_logement", period)

        return where(
            typologie_logement == TypologieLogement.maisonderetraite,
            montant,
            where(loyer <= loyer_mensuel_plafond, montant, 0),
        )
