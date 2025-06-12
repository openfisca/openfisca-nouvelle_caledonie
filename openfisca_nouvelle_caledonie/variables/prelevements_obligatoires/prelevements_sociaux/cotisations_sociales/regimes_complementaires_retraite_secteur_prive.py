from openfisca_core.model_api import *
from openfisca_nouvelle_caledonie.entities import Person as Individu
from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.prelevements_sociaux.cotisations_sociales.helpers import (
    apply_bareme,
    apply_bareme_for_relevant_type_sal,
)
from openfisca_nouvelle_caledonie.variables.prelevements_obligatoires.prelevements_sociaux.cotisations_sociales.salarie import (
    TypesCategorieSalarie,
)


class agff_salarie(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation retraite AGFF tranche A (salarié)"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    end = "2018-12-31"
    # AGFF: Association pour la gestion du fonds de financement (sous-entendu des départs entre 60 et 65 ans)

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="salarie",
            bareme_name="agff",
            variable_name="agff_salarie",
        )
        return cotisation


class agff_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation retraite AGFF tranche A (employeur)"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    end = "2018-12-31"
    # TODO: améliorer pour gérer mensuel/annuel

    def formula(individu, period, parameters):
        assiette_cotisations_sociales = individu(
            "assiette_cotisations_sociales", period
        )
        categorie_salarie = individu("categorie_salarie", period)
        plafond_securite_sociale = individu("plafond_securite_sociale", period)

        parameters = parameters(period).cotsoc

        cotisation_non_cadre = apply_bareme_for_relevant_type_sal(
            bareme_by_categorie_salarie=parameters.cotisations_employeur,
            bareme_name="agffnc",
            base=assiette_cotisations_sociales,
            plafond=plafond_securite_sociale,
            categorie_salarie=categorie_salarie,
        )

        cotisation_cadre = apply_bareme_for_relevant_type_sal(
            bareme_by_categorie_salarie=parameters.cotisations_employeur,
            bareme_name="agffc",
            base=assiette_cotisations_sociales,
            plafond=plafond_securite_sociale,
            categorie_salarie=categorie_salarie,
        )
        return cotisation_cadre + cotisation_non_cadre


class agirc_gmp_salarie(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation AGIRC pour la garantie minimale de points (GMP,  salarié)"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    end = "2018-12-31"
    # TODO: gestion annuel/mensuel

    def formula(individu, period, parameters):
        agirc_salarie = individu("agirc_salarie", period)
        assiette_cotisations_sociales = individu(
            "assiette_cotisations_sociales", period
        )
        categorie_salarie = individu("categorie_salarie", period)
        quotite = individu("quotite_de_travail", period)

        cadre_cotisant = (categorie_salarie == TypesCategorieSalarie.prive_cadre) & (
            assiette_cotisations_sociales > 0
        )

        gmp = parameters(
            period
        ).prelevements_obligatoires.prelevements_sociaux.regimes_complementaires_retraite_secteur_prive.gmp
        cotisation_forfaitaire_temps_plein = (
            gmp.cotisation_forfaitaire_mensuelle.part_salariale
        )
        cotisation_forfaitaire = cotisation_forfaitaire_temps_plein * quotite

        # Sachant:
        # - qu'il faut retourner un nombre négatif car c'est un prélèvement,
        # - que la cotisation agirc_salarie est négative car c'est un prélèvement,
        # - que la cotisation_forfaitaire est positive,
        # le montant de la gmp est cotisation_forfaitaire - (-agirc_salarie) soit:
        return -max_(cotisation_forfaitaire + agirc_salarie, 0) * cadre_cotisant


class agirc_gmp_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation AGIRC pour la garantie minimale de points (GMP, employeur)"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    end = "2018-12-31"
    # TODO: gestion annuel/mensuel

    def formula(individu, period, parameters):
        agirc_employeur = individu("agirc_employeur", period)
        assiette_cotisations_sociales = individu(
            "assiette_cotisations_sociales", period
        )
        categorie_salarie = individu("categorie_salarie", period)
        quotite = individu("quotite_de_travail", period)

        cadre_cotisant = (categorie_salarie == TypesCategorieSalarie.prive_cadre) & (
            assiette_cotisations_sociales > 0
        )

        gmp = parameters(
            period
        ).prelevements_obligatoires.prelevements_sociaux.regimes_complementaires_retraite_secteur_prive.gmp
        cotisation_forfaitaire_temps_plein = (
            gmp.cotisation_forfaitaire_mensuelle.part_patronale
        )
        cotisation_forfaitaire = cotisation_forfaitaire_temps_plein * quotite

        # Sachant:
        # - qu'il faut retourner un nombre négatif car c'est un prélèvement,
        # - que la cotisation agirc_salarie est négative car c'est un prélèvement,
        # - que la cotisation_forfaitaire est positive,
        # le montant de la gmp est cotisation_forfaitaire - (-agirc_salarie) soit:
        return -max_(cotisation_forfaitaire + agirc_employeur, 0) * cadre_cotisant


class agirc_salarie(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation AGIRC tranche B (salarié)"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    end = "2018-12-31"

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="salarie",
            bareme_name="agirc",
            variable_name="agirc_salarie",
        )
        categorie_salarie = individu("categorie_salarie", period)
        return cotisation * (categorie_salarie == TypesCategorieSalarie.prive_cadre)


class agirc_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation AGIRC tranche B (employeur)"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    end = "2018-12-31"

    def formula(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="employeur",
            bareme_name="agirc",
            variable_name="agirc_employeur",
        )
        categorie_salarie = individu("categorie_salarie", period)
        return cotisation * (categorie_salarie == TypesCategorieSalarie.prive_cadre)


class agirc_arrco_salarie(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation AGIRC-ARRCO (après la fusion, salarié)"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula_2019_01_01(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="salarie",
            bareme_name="agirc_arrco",
            variable_name="agirc_arrco_salarie",
        )
        return cotisation


class agirc_arrco_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation AGIRC-ARRCO (après la fusion, employeur)"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula_2019_01_01(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="employeur",
            bareme_name="agirc_arrco",
            variable_name="agirc_arrco_employeur",
        )
        return cotisation


class arrco_salarie(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation ARRCO tranche 1 (salarié)"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    end = "2018-12-31"
    # TODO: check gestion mensuel/annuel

    def formula(individu, period, parameters):
        cotisation_minimale = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="salarie",
            bareme_name="arrco",
            variable_name="arrco_salarie",
        )
        arrco_tranche_a_taux_salarie = individu("arrco_tranche_a_taux_salarie", period)
        assiette_cotisations_sociales = individu(
            "assiette_cotisations_sociales", period, options=[ADD]
        )
        plafond_securite_sociale = individu(
            "plafond_securite_sociale", period, options=[ADD]
        )
        categorie_salarie = individu("categorie_salarie", period)

        # cas où l'entreprise applique un taux spécifique
        cotisation_entreprise = -(
            min_(max_(assiette_cotisations_sociales, 0), plafond_securite_sociale)
            * arrco_tranche_a_taux_salarie
        )

        prive = (categorie_salarie == TypesCategorieSalarie.prive_non_cadre) + (
            categorie_salarie == TypesCategorieSalarie.prive_cadre
        )

        return (
            cotisation_minimale * (arrco_tranche_a_taux_salarie == 0)
            + cotisation_entreprise
        ) * prive


class arrco_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Cotisation ARRCO tranche 1 (employeur)"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    end = "2018-12-31"
    # TODO: check gestion mensuel/annuel

    def formula(individu, period, parameters):
        cotisation_minimale = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="employeur",
            bareme_name="arrco",
            variable_name="arrco_employeur",
        )
        arrco_tranche_a_taux_employeur = individu(
            "arrco_tranche_a_taux_employeur", period
        )
        assiette_cotisations_sociales = individu(
            "assiette_cotisations_sociales", period, options=[ADD]
        )
        plafond_securite_sociale = individu(
            "plafond_securite_sociale", period, options=[ADD]
        )
        categorie_salarie = individu("categorie_salarie", period)

        # cas où l'entreprise applique un taux spécifique
        cotisation_entreprise = -(
            min_(max_(assiette_cotisations_sociales, 0), plafond_securite_sociale)
            * arrco_tranche_a_taux_employeur
        )

        prive = (categorie_salarie == TypesCategorieSalarie.prive_non_cadre) + (
            categorie_salarie == TypesCategorieSalarie.prive_cadre
        )
        return (
            cotisation_minimale * (arrco_tranche_a_taux_employeur == 0)
            + cotisation_entreprise
        ) * prive


class contribution_equilibre_general_salarie(Variable):
    value_type = float
    entity = Individu
    label = "Contribution d'équilibre général (salarie)"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula_2019_01_01(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="salarie",
            bareme_name="ceg",
            variable_name="contribution_equilibre_general_salarie",
        )
        return cotisation


class contribution_equilibre_general_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Contribution d'équilibre général (employeur)"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula_2019_01_01(individu, period, parameters):
        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="employeur",
            bareme_name="ceg",
            variable_name="contribution_equilibre_general_employeur",
        )
        return cotisation


class contribution_equilibre_technique_salarie(Variable):
    value_type = float
    entity = Individu
    label = "Contribution d'équilibre technique (salarie)"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula_2019_01_01(individu, period, parameters):
        plafond_securite_sociale = individu("plafond_securite_sociale", period)
        assiette_cotisations_sociales = individu(
            "assiette_cotisations_sociales", period
        )

        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="salarie",
            bareme_name="cet2019",
            variable_name="contribution_equilibre_technique_salarie",
        )
        return cotisation * (assiette_cotisations_sociales > plafond_securite_sociale)


class contribution_equilibre_technique_employeur(Variable):
    value_type = float
    entity = Individu
    label = "Contribution d'équilibre technique (employeur)"
    definition_period = MONTH
    set_input = set_input_divide_by_period

    def formula_2019_01_01(individu, period, parameters):
        plafond_securite_sociale = individu("plafond_securite_sociale", period)
        assiette_cotisations_sociales = individu(
            "assiette_cotisations_sociales", period
        )

        cotisation = apply_bareme(
            individu,
            period,
            parameters,
            cotisation_type="employeur",
            bareme_name="cet2019",
            variable_name="contribution_equilibre_technique_employeur",
        )
        return cotisation * (assiette_cotisations_sociales > plafond_securite_sociale)
