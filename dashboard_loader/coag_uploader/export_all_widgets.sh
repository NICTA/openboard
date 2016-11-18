#!/bin/bash

# Housing Hero Widgets
echo "Exporting Housing Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_remote-housing-hero > coag_uploader/exports/03_remote_indigenous_housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_overcrowding-housing-hero > coag_uploader/exports/03_indigenous_overcrowding-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_homeownership-housing-hero > coag_uploader/exports/03_indigenous_homeownership-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag homelessness-housing-hero > coag_uploader/exports/03_homelessness-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag rentalstress-housing-hero > coag_uploader/exports/03_rentalstress-housing-hero.json

echo "Exporting Housing Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_remote-housing-hero-state > coag_uploader/exports/03_remote_indigenous_housing-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_overcrowding-housing-hero-state > coag_uploader/exports/03_indigenous_overcrowding-housing-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_homeownership-housing-hero-state > coag_uploader/exports/03_indigenous_homeownership-housing-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag homelessness-housing-hero-state > coag_uploader/exports/03_homelessness-housing-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag rentalstress-housing-hero-state > coag_uploader/exports/03_rentalstress-housing-hero-state.json

# Education Hero Widgets
echo "Exporting Education Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag yr12-education-hero > coag_uploader/exports/03_yr12-education-hero.json

# Skills Hero Widgets
echo "Exporting Skills Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag cert3-skills-hero > coag_uploader/exports/03_cert3-skills-hero.json

echo "Exporting Skills Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag cert3-skills-hero-state > coag_uploader/exports/03_cert3-skills-hero-state.json

# Health Hero Widgets
echo "Exporting Health Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag life_expectancy-health-hero > coag_uploader/exports/03_life_expectancy-health-hero.json

# Disability Hero Widgets
echo "Exporting Disability Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag social_participation-disability-hero > coag_uploader/exports/03_social_participation-disability-hero.json

# Indigenous Hero Widgets
# Infrastructure Hero Widgets
# Legal Assistance Hero Widgets

# Housing Detail Widgets
echo "Exporting Housing Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_indigenous_overcrowding > coag_uploader/exports/03_indigenous_overcrowding.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_indigenous_homeownership > coag_uploader/exports/03_indigenous_homeownership.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_homelessness > coag_uploader/exports/03_homelessness.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_rentalstress > coag_uploader/exports/03_rentalstress.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_homelessness_npa > coag_uploader/exports/03_homelessness_npa.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_remote_indigenous > coag_uploader/exports/03_remote_indigenous_housing.json

echo "Exporting Housing State Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_indigenous_overcrowding_state > coag_uploader/exports/03_indigenous_overcrowding-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_indigenous_homeownership_state > coag_uploader/exports/03_indigenous_homeownership-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_rentalstress_state > coag_uploader/exports/03_rentalstress-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_homelessness_state > coag_uploader/exports/03_homelessness-state.json

# Education Detail Widgets
# Skills Detail Widgets
# Health Detail Widgets
# Disability Detail Widgets
# Indigenous Detail Widgets
# Infrastructure Detail Widgets
# Legal Assistance Detail Widgets

echo "Done."
