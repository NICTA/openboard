#!/bin/bash

# Housing Hero Widgets  wdef sort_order 0, 5, ... 100, 105, ...
echo "Exporting Housing Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag homelessness_npa-housing-hero > coag_uploader/exports/03_homelessness_npa-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_remote-housing-hero > coag_uploader/exports/03_remote_indigenous_housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_overcrowding-housing-hero > coag_uploader/exports/03_indigenous_overcrowding-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_homeownership-housing-hero > coag_uploader/exports/03_indigenous_homeownership-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag homelessness-housing-hero > coag_uploader/exports/03_homelessness-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag rentalstress-housing-hero > coag_uploader/exports/03_rentalstress-housing-hero.json

echo "Exporting Housing Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag homelessness_npa-housing-hero-state > coag_uploader/exports/03_homelessness_npa-housing-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_remote-housing-hero-state > coag_uploader/exports/03_remote_indigenous_housing-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_overcrowding-housing-hero-state > coag_uploader/exports/03_indigenous_overcrowding-housing-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_homeownership-housing-hero-state > coag_uploader/exports/03_indigenous_homeownership-housing-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag homelessness-housing-hero-state > coag_uploader/exports/03_homelessness-housing-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag rentalstress-housing-hero-state > coag_uploader/exports/03_rentalstress-housing-hero-state.json

# Education Hero Widgets  wdef sort_order 200, 205, ... 300, 305, ...
echo "Exporting Education Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag yr12-education-hero > coag_uploader/exports/03_yr12-education-hero.json

echo "Exporting Education Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag yr12-education-hero-state > coag_uploader/exports/03_yr12-education-hero-state.json

# Skills Hero Widgets  wdef sort_order 400, 405, ... 500, 505, ...
echo "Exporting Skills Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag cert3-skills-hero > coag_uploader/exports/03_cert3-skills-hero.json

echo "Exporting Skills Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag cert3-skills-hero-state > coag_uploader/exports/03_cert3-skills-hero-state.json

# Health Hero Widgets wdef sort_order 600, 605, ... 700, 705, ...
echo "Exporting Health Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag life_expectancy-health-hero > coag_uploader/exports/03_life_expectancy-health-hero.json

echo "Exporting Health Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag life_expectancy-health-hero-state > coag_uploader/exports/03_life_expectancy-health-hero-state.json

# Disability Hero Widgets wdef sort_order 800, 805, ... 900, 905, ...
echo "Exporting Disability Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag social_participation-disability-hero > coag_uploader/exports/03_social_participation-disability-hero.json

echo "Exporting Disability Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag social_participation-disability-hero-state > coag_uploader/exports/03_social_participation-disability-hero-state.json

# Indigenous Hero Widgets       wdef sort_order 1000, 1005, ... 1100, 1105, ...
# Infrastructure Hero Widgets   wdef sort_order 1200, 1205, ... 1300, 1305, ...
# Legal Assistance Hero Widgets wdef sort_order 1400, 1405, ... 1500, 1505, ...


# Housing Detail Widgets  wdef sort_order 2000, 2005, ... 2100, 2105, ...
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
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_homelessness_npa_state > coag_uploader/exports/03_homelessness_npa-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_remote_indigenous_state > coag_uploader/exports/03_remote_indigenous_housing-state.json

# Education Detail Widgets   wdef sort_order 2200, 2005, ... 2300, 2105, ...
# Skills Detail Widgets      wdef sort_order 2400, 2205, ... 2500, 2305, ...
# Health Detail Widgets      wdef sort_order 2600, 2405, ... 2700, 2505, ...
# Disability Detail Widgets  wdef sort_order 2800, 2605, ... 2900, 2705, ...
# Indigenous Detail Widgets      wdef sort_order 3000, 3005, ... 3100, 3105, ...
# Infrastructure Detail Widgets  wdef sort_order 3200, 3205, ... 3300, 3305, ...
# Legal Assistance Detail Widgets  wdef sort_order 3400, 3405, ... 3500, 3505, ...

echo "Done."
