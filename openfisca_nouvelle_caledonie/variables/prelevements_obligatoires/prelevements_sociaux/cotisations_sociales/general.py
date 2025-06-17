from functools import partial

from numpy import busday_count as original_busday_count, datetime64, timedelta64, where

from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Individu


class plafond_fsh(Variable):
    value_type = float
    entity = Individu
    label = "Plafond applicable aux cotisations FSH"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    # TODO gérer les plafonds mensuel, trimestriel, annuel

    def formula(individu, period, parameters):
        plafond_temps_plein = parameters(
            period
        ).prelevements_obligatoires.prelevements_sociaux.fsh.plafond_mensuel
        quotite = individu("quotite_de_travail", period)

        plafond = plafond_temps_plein * quotite

        # 2) Proratisation pour mois incomplet selon la méthode des 30èmes

        # Pour les salariés entrés ou sortis en cours de mois,
        # le plafond applicable est égal à autant de trentièmes du plafond mensuel
        # que le salarié a été présent de jours calendaires. Source urssaf.fr "L’assiette maximale"
        # calcul du nombre de jours calendaires de présence du salarié
        nombre_jours_calendaires = individu("nombre_jours_calendaires", period)
        plafond = plafond * (min_(nombre_jours_calendaires, 30) / 30)

        # "Ce rapport ne peut pas conduire à un résultat supérieur à la valeur mensuelle du plafond de sécurité sociale."
        # Source : https://boss.gouv.fr/portail/accueil/regles-dassujettissement/assiette-generale.html#titre-chapitre-6---le-plafond-de-la-se-section-2---determination-de-las-a-principe-de-lajustement-a-due-2-salaries-a-temps-partiel
        # §810
        plafond = min_(plafond, plafond_temps_plein)

        return plafond

    # def formula_2023_09(individu, period, parameters):
    #     plafond_temps_plein = parameters(period).prelevements_obligatoires.prelevements_sociaux.fsh.plafond_mensuel
    #     quotite = individu('quotite_de_travail', period)
    #     renonciation_ajustement_pss_temps_partiel = individu('renonciation_ajustement_pss_temps_partiel', period)

    #     plafond = plafond_temps_plein * renonciation_ajustement_pss_temps_partiel + plafond_temps_plein * quotite * not_(renonciation_ajustement_pss_temps_partiel)

    #     # 2) Proratisation pour mois incomplet selon la méthode des 30èmes

    #     # Pour les salariés entrés ou sortis en cours de mois,
    #     # le plafond applicable est égal à autant de trentièmes du plafond mensuel
    #     # que le salarié a été présent de jours calendaires. Source urssaf.fr "L’assiette maximale"
    #     # calcul du nombre de jours calendaires de présence du salarié
    #     nombre_jours_calendaires = individu('nombre_jours_calendaires', period)
    #     plafond = plafond * (min_(nombre_jours_calendaires, 30) / 30)

    #     # "Ce rapport ne peut pas conduire à un résultat supérieur à la valeur mensuelle du plafond de sécurité sociale."
    #     # Source : https://boss.gouv.fr/portail/accueil/regles-dassujettissement/assiette-generale.html#titre-chapitre-6---le-plafond-de-la-se-section-2---determination-de-las-a-principe-de-lajustement-a-due-2-salaries-a-temps-partiel
    #     # §810
    #     plafond = min_(plafond, plafond_temps_plein)

    #     return plafond


class plafond_cafat_autres_regimes(Variable):
    value_type = float
    entity = Individu
    label = "Plafond applicable aux cotisations CAFAT autres régimes"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    # TODO gérer les plafonds mensuel, trimestriel, annuel

    def formula(individu, period, parameters):
        plafond_temps_plein = parameters(
            period
        ).prelevements_obligatoires.prelevements_sociaux.cafat.autres_regimes.plafond_mensuel
        quotite = individu("quotite_de_travail", period)

        plafond = plafond_temps_plein * quotite

        # 2) Proratisation pour mois incomplet selon la méthode des 30èmes

        # Pour les salariés entrés ou sortis en cours de mois,
        # le plafond applicable est égal à autant de trentièmes du plafond mensuel
        # que le salarié a été présent de jours calendaires. Source urssaf.fr "L’assiette maximale"
        # calcul du nombre de jours calendaires de présence du salarié
        nombre_jours_calendaires = individu("nombre_jours_calendaires", period)
        plafond = plafond * (min_(nombre_jours_calendaires, 30) / 30)

        # "Ce rapport ne peut pas conduire à un résultat supérieur à la valeur mensuelle du plafond de sécurité sociale."
        # Source : https://boss.gouv.fr/portail/accueil/regles-dassujettissement/assiette-generale.html#titre-chapitre-6---le-plafond-de-la-se-section-2---determination-de-las-a-principe-de-lajustement-a-due-2-salaries-a-temps-partiel
        # §810
        plafond = min_(plafond, plafond_temps_plein)

        return plafond

    # def formula_2023_09(individu, period, parameters):
    #     plafond_temps_plein = parameters(period).prelevements_obligatoires.prelevements_sociaux.pss.plafond_securite_sociale_mensuel
    #     quotite = individu('quotite_de_travail', period)
    #     renonciation_ajustement_pss_temps_partiel = individu('renonciation_ajustement_pss_temps_partiel', period)

    #     plafond = plafond_temps_plein * renonciation_ajustement_pss_temps_partiel + plafond_temps_plein * quotite * not_(renonciation_ajustement_pss_temps_partiel)

    #     # 2) Proratisation pour mois incomplet selon la méthode des 30èmes

    #     # Pour les salariés entrés ou sortis en cours de mois,
    #     # le plafond applicable est égal à autant de trentièmes du plafond mensuel
    #     # que le salarié a été présent de jours calendaires. Source urssaf.fr "L’assiette maximale"
    #     # calcul du nombre de jours calendaires de présence du salarié
    #     nombre_jours_calendaires = individu('nombre_jours_calendaires', period)
    #     plafond = plafond * (min_(nombre_jours_calendaires, 30) / 30)

    #     # "Ce rapport ne peut pas conduire à un résultat supérieur à la valeur mensuelle du plafond de sécurité sociale."
    #     # Source : https://boss.gouv.fr/portail/accueil/regles-dassujettissement/assiette-generale.html#titre-chapitre-6---le-plafond-de-la-se-section-2---determination-de-las-a-principe-de-lajustement-a-due-2-salaries-a-temps-partiel
    #     # §810
    #     plafond = min_(plafond, plafond_temps_plein)

    #     return plafond


class plafond_retraite(Variable):
    value_type = float
    entity = Individu
    label = "Plafond applicable aux cotisations retraite"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    # TODO gérer les plafonds mensuel, trimestriel, annuel

    def formula(individu, period, parameters):
        plafond_temps_plein = parameters(
            period
        ).prelevements_obligatoires.prelevements_sociaux.cafat.maladie_retraite.plafond_retraite_mensuel
        quotite = individu("quotite_de_travail", period)

        plafond = plafond_temps_plein * quotite

        # 2) Proratisation pour mois incomplet selon la méthode des 30èmes

        # Pour les salariés entrés ou sortis en cours de mois,
        # le plafond applicable est égal à autant de trentièmes du plafond mensuel
        # que le salarié a été présent de jours calendaires. Source urssaf.fr "L’assiette maximale"
        # calcul du nombre de jours calendaires de présence du salarié
        nombre_jours_calendaires = individu("nombre_jours_calendaires", period)
        plafond = plafond * (min_(nombre_jours_calendaires, 30) / 30)

        # "Ce rapport ne peut pas conduire à un résultat supérieur à la valeur mensuelle du plafond de sécurité sociale."
        # Source : https://boss.gouv.fr/portail/accueil/regles-dassujettissement/assiette-generale.html#titre-chapitre-6---le-plafond-de-la-se-section-2---determination-de-las-a-principe-de-lajustement-a-due-2-salaries-a-temps-partiel
        # §810
        plafond = min_(plafond, plafond_temps_plein)

        return plafond

    # def formula_2023_09(individu, period, parameters):
    #     plafond_temps_plein = parameters(period).prelevements_obligatoires.prelevements_sociaux.pss.plafond_securite_sociale_mensuel
    #     quotite = individu('quotite_de_travail', period)
    #     renonciation_ajustement_pss_temps_partiel = individu('renonciation_ajustement_pss_temps_partiel', period)

    #     plafond = plafond_temps_plein * renonciation_ajustement_pss_temps_partiel + plafond_temps_plein * quotite * not_(renonciation_ajustement_pss_temps_partiel)

    #     # 2) Proratisation pour mois incomplet selon la méthode des 30èmes

    #     # Pour les salariés entrés ou sortis en cours de mois,
    #     # le plafond applicable est égal à autant de trentièmes du plafond mensuel
    #     # que le salarié a été présent de jours calendaires. Source urssaf.fr "L’assiette maximale"
    #     # calcul du nombre de jours calendaires de présence du salarié
    #     nombre_jours_calendaires = individu('nombre_jours_calendaires', period)
    #     plafond = plafond * (min_(nombre_jours_calendaires, 30) / 30)

    #     # "Ce rapport ne peut pas conduire à un résultat supérieur à la valeur mensuelle du plafond de sécurité sociale."
    #     # Source : https://boss.gouv.fr/portail/accueil/regles-dassujettissement/assiette-generale.html#titre-chapitre-6---le-plafond-de-la-se-section-2---determination-de-las-a-principe-de-lajustement-a-due-2-salaries-a-temps-partiel
    #     # §810
    #     plafond = min_(plafond, plafond_temps_plein)

    #     return plafond


class plafond_securite_sociale(Variable):
    value_type = float
    entity = Individu
    label = "Plafond de la sécurite sociale"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    # TODO gérer les plafonds mensuel, trimestriel, annuel

    def formula(individu, period, parameters):
        plafond_temps_plein = parameters(
            period
        ).prelevements_obligatoires.prelevements_sociaux.pss.plafond_securite_sociale_mensuel
        quotite = individu("quotite_de_travail", period)

        plafond = plafond_temps_plein * quotite

        # 2) Proratisation pour mois incomplet selon la méthode des 30èmes

        # Pour les salariés entrés ou sortis en cours de mois,
        # le plafond applicable est égal à autant de trentièmes du plafond mensuel
        # que le salarié a été présent de jours calendaires. Source urssaf.fr "L’assiette maximale"
        # calcul du nombre de jours calendaires de présence du salarié
        nombre_jours_calendaires = individu("nombre_jours_calendaires", period)
        plafond = plafond * (min_(nombre_jours_calendaires, 30) / 30)

        # "Ce rapport ne peut pas conduire à un résultat supérieur à la valeur mensuelle du plafond de sécurité sociale."
        # Source : https://boss.gouv.fr/portail/accueil/regles-dassujettissement/assiette-generale.html#titre-chapitre-6---le-plafond-de-la-se-section-2---determination-de-las-a-principe-de-lajustement-a-due-2-salaries-a-temps-partiel
        # §810
        plafond = min_(plafond, plafond_temps_plein)

        return plafond

    # def formula_2023_09(individu, period, parameters):
    #     plafond_temps_plein = parameters(period).prelevements_obligatoires.prelevements_sociaux.pss.plafond_securite_sociale_mensuel
    #     quotite = individu('quotite_de_travail', period)
    #     renonciation_ajustement_pss_temps_partiel = individu('renonciation_ajustement_pss_temps_partiel', period)

    #     plafond = plafond_temps_plein * renonciation_ajustement_pss_temps_partiel + plafond_temps_plein * quotite * not_(renonciation_ajustement_pss_temps_partiel)

    #     # 2) Proratisation pour mois incomplet selon la méthode des 30èmes

    #     # Pour les salariés entrés ou sortis en cours de mois,
    #     # le plafond applicable est égal à autant de trentièmes du plafond mensuel
    #     # que le salarié a été présent de jours calendaires. Source urssaf.fr "L’assiette maximale"
    #     # calcul du nombre de jours calendaires de présence du salarié
    #     nombre_jours_calendaires = individu('nombre_jours_calendaires', period)
    #     plafond = plafond * (min_(nombre_jours_calendaires, 30) / 30)

    #     # "Ce rapport ne peut pas conduire à un résultat supérieur à la valeur mensuelle du plafond de sécurité sociale."
    #     # Source : https://boss.gouv.fr/portail/accueil/regles-dassujettissement/assiette-generale.html#titre-chapitre-6---le-plafond-de-la-se-section-2---determination-de-las-a-principe-de-lajustement-a-due-2-salaries-a-temps-partiel
    #     # §810
    #     plafond = min_(plafond, plafond_temps_plein)

    #     return plafond


class quotite_de_travail(Variable):
    value_type = float
    entity = Individu
    label = "Quotité de travail"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    # TODO: gestion annuel/mensuel

    def formula(individu, period, parameters):
        contrat_de_travail = individu("contrat_de_travail", period)
        TypesContratDeTravail = contrat_de_travail.possible_values
        parameters = parameters(period)
        heures_temps_plein = 169  # TODO: parameters
        # heures_temps_plein = parameters.marche_travail.salaire_minimum.smic.nb_heures_travail_mensuel
        # forfait_jours_remuneres_volume = individu('forfait_jours_remuneres_volume', period)
        heures_remunerees_volume = individu("heures_remunerees_volume", period)
        return switch(
            contrat_de_travail,
            {
                TypesContratDeTravail.temps_plein: 1,
                TypesContratDeTravail.temps_partiel: (
                    heures_remunerees_volume / heures_temps_plein
                ),
                # TypesContratDeTravail.forfait_jours_annee: (forfait_jours_remuneres_volume / 218),
                # TypesContratDeTravail.sans_objet: 0
            },
        )


class TypesContratDeTravail(Enum):
    __order__ = "temps_plein temps_partiel forfait_heures_semaines forfait_heures_mois forfait_heures_annee forfait_jours_annee sans_objet"  # Needed to preserve the enum order in Python 2
    temps_plein = "Temps plein"
    temps_partiel = "Temps partiel"
    forfait_heures_semaines = "Convention de forfait heures sur la semaine"
    forfait_heures_mois = "Convention de forfait heures sur le mois"
    forfait_heures_annee = "Convention de forfait heures sur l’année"
    forfait_jours_annee = "Convention de forfait jours sur l’année"
    sans_objet = "Non renseigné"


class contrat_de_travail(Variable):
    value_type = Enum
    possible_values = TypesContratDeTravail
    default_value = TypesContratDeTravail.temps_plein
    entity = Individu
    label = "Type de durée de travail"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class heures_remunerees_volume(Variable):
    # N'est pas pris en compte lorsque type_contrat_travail = temps_plein
    value_type = float
    entity = Individu
    label = "Volume des heures rémunérées contractuellement"
    set_input = set_input_divide_by_period
    definition_period = MONTH


class nombre_jours_calendaires(Variable):
    value_type = float
    entity = Individu
    label = "Nombre de jours calendaires travaillés"
    definition_period = MONTH
    default_value = 30
    set_input = set_input_divide_by_period

    def formula(individu, period, parameters):
        contrat_de_travail_debut = individu("contrat_de_travail_debut", period)
        contrat_de_travail_fin = individu("contrat_de_travail_fin", period)

        busday_count = partial(original_busday_count, weekmask="1" * 7)
        debut_mois = datetime64(period.start.offset("first-of", "month"))
        fin_mois = datetime64(period.start.offset("last-of", "month"))
        jours_travailles = max_(
            busday_count(
                max_(contrat_de_travail_debut, debut_mois),
                min_(contrat_de_travail_fin, fin_mois) + timedelta64(1, "D"),
            ),
            0,
        )

        return jours_travailles


class contrat_de_travail_debut(Variable):
    value_type = date
    default_value = date(1870, 1, 1)
    entity = Individu
    label = "Date d'arrivée dans l'entreprise"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class contrat_de_travail_fin(Variable):
    value_type = date
    default_value = date(2099, 12, 31)
    entity = Individu
    label = "Date de départ de l'entreprise"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class arrco_tranche_a_taux_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Taux ARRCO tranche A employeur propre à l'entreprise"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class arrco_tranche_a_taux_salarie(Variable):
    value_type = float
    entity = Individu
    label = "Taux ARRCO tranche A salarié propre à l'entreprise"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class taux_accident_du_travail(Variable):
    value_type = float
    entity = Individu
    label = "Taux accident du travail"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period
