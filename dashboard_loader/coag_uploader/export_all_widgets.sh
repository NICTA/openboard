#!/bin/bash

# Housing Hero Widgets  wdef sort_order 0, 5, ... 100, 105, ...
echo "Exporting Housing Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag homelessness_npa-housing-hero > coag_uploader/exports/03_homelessness_npa-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_remote-housing-hero > coag_uploader/exports/03_remote_indigenous_housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_overcrowding-housing-hero > coag_uploader/exports/03_indigenous_overcrowding-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_homeownership-housing-hero > coag_uploader/exports/03_indigenous_homeownership-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag homelessness-housing-hero > coag_uploader/exports/03_homelessness-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag rentalstress-housing-hero > coag_uploader/exports/03_rentalstress-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag remote_condition-housing-hero > coag_uploader/exports/03_remote_condition-housing-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag remote_overcrowding-housing-hero > coag_uploader/exports/03_remote_overcrowding-housing-hero.json

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
python manage.py export_widget --settings=dashboard_loader.settings_coag yr12_2015-education-hero > coag_uploader/exports/03_yr12_2015-education-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag naplan_lit-education-hero > coag_uploader/exports/03_naplan_lit-education-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag naplan_num-education-hero > coag_uploader/exports/03_naplan_num-education-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag participation-education-hero > coag_uploader/exports/03_participation-education-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag ecenqs-education-hero > coag_uploader/exports/03_ecenqs-education-hero.json

echo "Exporting Education Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag yr12-education-hero-state > coag_uploader/exports/03_yr12-education-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag yr12_2015-education-hero-state > coag_uploader/exports/03_yr12_2015-education-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag naplan_lit-education-hero-state > coag_uploader/exports/03_naplan_lit-education-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag naplan_num-education-hero-state > coag_uploader/exports/03_naplan_num-education-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag participation-education-hero-state > coag_uploader/exports/03_participation-education-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag ecenqs-education-hero-state > coag_uploader/exports/03_ecenqs-education-hero-state.json

# Skills Hero Widgets  wdef sort_order 400, 405, ... 500, 505, ...
echo "Exporting Skills Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag cert3-skills-hero > coag_uploader/exports/03_cert3-skills-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag higher_qual-skills-hero > coag_uploader/exports/03_higher_qual-skills-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag improved_employ-skills-hero > coag_uploader/exports/03_improved_employ-skills-hero.json

echo "Exporting Skills Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag cert3-skills-hero-state > coag_uploader/exports/03_cert3-skills-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag higher_qual-skills-hero-state > coag_uploader/exports/03_higher_qual-skills-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag improved_employ-skills-hero-state > coag_uploader/exports/03_improved_employ-skills-hero-state.json

# Health Hero Widgets wdef sort_order 600, 605, ... 700, 705, ...
echo "Exporting Health Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag life_expectancy-health-hero > coag_uploader/exports/03_life_expectancy-health-hero.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag diabetes-health-hero > coag_uploader/exports/03_diabetes-health-hero.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag healthyweight-health-hero > coag_uploader/exports/03_healthyweight-health-hero.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag childweight-health-hero > coag_uploader/exports/03_childhealthyweight-health-hero.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag smoking-health-hero > coag_uploader/exports/03_smoking-health-hero.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag indig_smoking-health-hero > coag_uploader/exports/03_indig_smoking-health-hero.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag edwait-health-hero > coag_uploader/exports/03_edwait-health-hero.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag gpwait-health-hero > coag_uploader/exports/03_gpwait-health-hero.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag avoidable-health-hero > coag_uploader/exports/03_avoidable-health-hero.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag agedcare-health-hero > coag_uploader/exports/03_agedcare_places-health-hero.json 

echo "Exporting Health Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag life_expectancy-health-hero-state > coag_uploader/exports/03_life_expectancy-health-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag diabetes-health-hero-state > coag_uploader/exports/03_diabetes-health-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag healthyweight-health-hero-state > coag_uploader/exports/03_healthyweight-health-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag childweight-health-hero-state > coag_uploader/exports/03_childweight-health-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag smoking-health-hero-state > coag_uploader/exports/03_smoking-health-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indig_smoking-health-hero-state > coag_uploader/exports/03_indig_smoking-health-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag edwait-health-hero-state > coag_uploader/exports/03_edwait-health-hero-state.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag gpwait-health-hero-state > coag_uploader/exports/03_gpwait-health-hero-state.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag avoidable-health-hero-state > coag_uploader/exports/03_avoidable-health-hero-state.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag agedcare-health-hero-state > coag_uploader/exports/03_agedcare_places-health-hero-state.json 

# Disability Hero Widgets wdef sort_order 800, 805, ... 900, 905, ...
echo "Exporting Disability Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag labour_participation-disability-hero > coag_uploader/exports/03_labour_participation-disability-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag social_participation-disability-hero > coag_uploader/exports/03_social_participation-disability-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag more_assist-disability-hero > coag_uploader/exports/03_more_assist-disability-hero.json

echo "Exporting Disability Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag labour_participation-disability-hero-state > coag_uploader/exports/03_labour_participation-disability-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag social_participation-disability-hero-state > coag_uploader/exports/03_social_participation-disability-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag more_assist-disability-hero-state > coag_uploader/exports/03_more_assist-disability-hero-state.json

# Indigenous Hero Widgets       wdef sort_order 1000, 1005, ... 1100, 1105, ...
echo "Exporting Indigenous Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag child_mortality-indigenous-hero > coag_uploader/exports/03_child_mortality-indigenous-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indig_ece-indigenous-hero > coag_uploader/exports/03_indig_ece-indigenous-hero.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indig_employment-indigenous-hero > coag_uploader/exports/03_indig_employment-indigenous-hero.json

echo "Exporting Indigenous Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag child_mortality-indigenous-hero-state > coag_uploader/exports/03_child_mortality-indigenous-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indig_ece-indigenous-hero-state > coag_uploader/exports/03_indig_ece-indigenous-hero-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indig_employment-indigenous-hero-state > coag_uploader/exports/03_indig_employment-indigenous-hero-state.json

# Infrastructure Hero Widgets   wdef sort_order 1200, 1205, ... 1300, 1305, ...
echo "Exporting Infrastructure Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag projects-infrastructure-hero > coag_uploader/exports/03_projects-infrastructure-hero.json

echo "Exporting Infrastructure Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag projects-infrastructure-hero-state > coag_uploader/exports/03_projects-infrastructure-hero-state.json

# Legal Assistance Hero Widgets wdef sort_order 1400, 1405, ... 1500, 1505, ...
echo "Exporting Legal Assistance Hero Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag total_svc-legal-hero > coag_uploader/exports/03_total_svc-legal-hero.json

echo "Exporting Legal Assistance Hero Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag total_svc-legal-hero-state > coag_uploader/exports/03_total_svc-legal-hero-state.json


# Housing Detail Widgets  wdef sort_order 2000, 2005, ... 2100, 2105, ...
echo "Exporting Housing Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_indigenous_overcrowding > coag_uploader/exports/03_indigenous_overcrowding.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_indigenous_homeownership > coag_uploader/exports/03_indigenous_homeownership.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_homelessness > coag_uploader/exports/03_homelessness.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_rentalstress > coag_uploader/exports/03_rentalstress.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_homelessness_npa > coag_uploader/exports/03_homelessness_npa.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_remote_indigenous > coag_uploader/exports/03_remote_indigenous_housing.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_remote_condition > coag_uploader/exports/03_remote_condition.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_remote_overcrowding > coag_uploader/exports/03_remote_overcrowding.json

echo "Exporting Housing State Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_indigenous_overcrowding_state > coag_uploader/exports/03_indigenous_overcrowding-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_indigenous_homeownership_state > coag_uploader/exports/03_indigenous_homeownership-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_rentalstress_state > coag_uploader/exports/03_rentalstress-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_homelessness_state > coag_uploader/exports/03_homelessness-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_homelessness_npa_state > coag_uploader/exports/03_homelessness_npa-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag housing_remote_indigenous_state > coag_uploader/exports/03_remote_indigenous_housing-state.json

# Education Detail Widgets   wdef sort_order 2200, 2205, ... 2300, 2305, ...
echo "Exporting Eduation Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag education_yr12 > coag_uploader/exports/03_yr12.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_yr12_2015 > coag_uploader/exports/03_yr12_2015.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_naplan_lit > coag_uploader/exports/03_naplan_lit.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_naplan_num > coag_uploader/exports/03_naplan_num.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_participation > coag_uploader/exports/03_participation.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_ecenqs > coag_uploader/exports/03_ecenqs.json

echo "Exporting Education State Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag education_yr12_state > coag_uploader/exports/03_yr12-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_yr12_2015_state > coag_uploader/exports/03_yr12_2015-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_naplan_lit_state > coag_uploader/exports/03_naplan_lit-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_naplan_num_state > coag_uploader/exports/03_naplan_num-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_participation_state > coag_uploader/exports/03_participation-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag education_ecenqs_state > coag_uploader/exports/03_ecenqs-state.json

# Skills Detail Widgets      wdef sort_order 2400, 2405, ... 2500, 2505, ...
echo "Exporting Skills Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag skills_cert3 > coag_uploader/exports/03_cert3.json
python manage.py export_widget --settings=dashboard_loader.settings_coag skills_higher_qual > coag_uploader/exports/03_higher_qual.json
python manage.py export_widget --settings=dashboard_loader.settings_coag skills_improved_employ > coag_uploader/exports/03_improved_employ.json

echo "Exporting Skills Detail Widgets (Parametised by State)"
python manage.py export_widget --settings=dashboard_loader.settings_coag skills_cert3_state > coag_uploader/exports/03_cert3-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag skills_higher_qual_state > coag_uploader/exports/03_higher_qual-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag skills_improved_employ_state > coag_uploader/exports/03_improved_employ-state.json

# Health Detail Widgets      wdef sort_order 2600, 2605, ... 2700, 2705, ...
echo "Exporting Health Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag health_life_expectancy > coag_uploader/exports/03_life_expectancy.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_diabetes > coag_uploader/exports/03_diabetes.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_healthyweight > coag_uploader/exports/03_healthyweight.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_childweight > coag_uploader/exports/03_childhealthyweight.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_smoking > coag_uploader/exports/03_smoking.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_indig_smoking > coag_uploader/exports/03_indig_smoking.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_edwait > coag_uploader/exports/03_edwait.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag health_gpwait > coag_uploader/exports/03_gpwait.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag health_avoidable > coag_uploader/exports/03_avoidable.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag health_agedcare > coag_uploader/exports/03_agedcare_places.json 

echo "Exporting Health State Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag health_life_expectancy_state > coag_uploader/exports/03_life_expectancy-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_diabetes_state > coag_uploader/exports/03_diabetes-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_healthyweight_state > coag_uploader/exports/03_healthyweight-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_childweight_state > coag_uploader/exports/03_childhealthyweight-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_smoking_state > coag_uploader/exports/03_smoking-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_indig_smoking_state > coag_uploader/exports/03_indig_smoking-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag health_edwait_state > coag_uploader/exports/03_edwait-state.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag health_gpwait_state > coag_uploader/exports/03_gpwait-state.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag health_avoidable_state > coag_uploader/exports/03_avoidable-state.json 
python manage.py export_widget --settings=dashboard_loader.settings_coag health_agedcare_state > coag_uploader/exports/03_agedcare_places-state.json 

# Disability Detail Widgets  wdef sort_order 2800, 2805, ... 2900, 2905, ...
echo "Exporting Disability Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag disability_labour_participation > coag_uploader/exports/03_labour_participation.json
python manage.py export_widget --settings=dashboard_loader.settings_coag disability_social_participation > coag_uploader/exports/03_social_participation.json
python manage.py export_widget --settings=dashboard_loader.settings_coag disability_more_assist > coag_uploader/exports/03_more_assist.json

echo "Exporting Disability State Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag disability_labour_participation_state > coag_uploader/exports/03_labour_participation-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag disability_social_participation_state > coag_uploader/exports/03_social_participation-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag disability_more_assist_state > coag_uploader/exports/03_more_assist-state.json

# Indigenous Detail Widgets      wdef sort_order 3000, 3005, ... 3100, 3105, ...
echo "Exporting Indigenous Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_child_mortality > coag_uploader/exports/03_child_mortality.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_indig_ece > coag_uploader/exports/03_indig_ece.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_indig_employment > coag_uploader/exports/03_indig_employment.json

echo "Exporting Indigenous State Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_child_mortality_state > coag_uploader/exports/03_child_mortality-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_indig_ece_state > coag_uploader/exports/03_indig_ece-state.json
python manage.py export_widget --settings=dashboard_loader.settings_coag indigenous_indig_employment_state > coag_uploader/exports/03_indig_employment-state.json


# Infrastructure Detail Widgets  wdef sort_order 3200, 3205, ... 3300, 3305, ...
echo "Exporting Infrastructure Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag infrastructure_projects > coag_uploader/exports/03_projects.json

echo "Exporting Infrastructure State Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag infrastructure_projects_state > coag_uploader/exports/03_projects-state.json

# Legal Assistance Detail Widgets  wdef sort_order 3400, 3405, ... 3500, 3505, ...
echo "Exporting Legal Assistance Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag legal_total_svc > coag_uploader/exports/03_total_svc.json

echo "Exporting Legal Assistance Detail Widgets"
python manage.py export_widget --settings=dashboard_loader.settings_coag legal_total_svc-state > coag_uploader/exports/03_total_svc-state.json

echo "Done."
