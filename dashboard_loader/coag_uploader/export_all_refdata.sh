#!/bin/bash

echo "Exporting Icon Libraries and Traffic Light Scales..."
python manage.py export_iconlibrary --settings=dashboard_loader.settings_coag indicator_benchmark_icons > coag_uploader/exports/01_icons_indicator_benchmark.json

python manage.py export_trafficlightscale --settings=dashboard_loader.settings_coag "Benchmark Scale" > coag_uploader/exports/01_tlc_benchmark.json
python manage.py export_trafficlightscale --settings=dashboard_loader.settings_coag "Indicator Scale" > coag_uploader/exports/01_tlc_indicator.json

echo "Exporting Views..."
python manage.py export_view --settings=dashboard_loader.settings_coag aus > coag_uploader/exports/01_views.json

echo "Exporting Categories..."
python manage.py export_categories --settings=dashboard_loader.settings_coag > coag_uploader/exports/02_categories.json

echo "Exporting View Families..."
python manage.py export_view_family --settings=dashboard_loader.settings_coag region_indexes > coag_uploader/exports/02_fv_region_indexes.json
python manage.py export_view_family --settings=dashboard_loader.settings_coag region_housing > coag_uploader/exports/02_fv_region_housing.json
python manage.py export_view_family --settings=dashboard_loader.settings_coag region_education > coag_uploader/exports/02_fv_region_education.json
python manage.py export_view_family --settings=dashboard_loader.settings_coag region_skills > coag_uploader/exports/02_fv_region_skills.json
python manage.py export_view_family --settings=dashboard_loader.settings_coag region_healthcare > coag_uploader/exports/02_fv_region_healthcare.json
python manage.py export_view_family --settings=dashboard_loader.settings_coag region_disability > coag_uploader/exports/02_fv_region_disability.json
python manage.py export_view_family --settings=dashboard_loader.settings_coag region_indigenous > coag_uploader/exports/02_fv_region_indigenous.json
python manage.py export_view_family --settings=dashboard_loader.settings_coag region_infrastructure > coag_uploader/exports/02_fv_region_infrastructure.json
python manage.py export_view_family --settings=dashboard_loader.settings_coag region_legal_assistance > coag_uploader/exports/02_fv_region_legal_assistance.json

echo "Exporting Parametisations..."
python manage.py export_parametisation --settings=dashboard_loader.settings_coag state_param > coag_uploader/exports/02_state_param.json

echo "Done."

