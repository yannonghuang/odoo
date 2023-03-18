# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Base report xml",
    "summary": "Base module to create xml report",
    "author": "",
    "website": "",
    "category": "Reporting",
    "version": "2.1",
    "development_status": "Mature",
    "license": "AGPL-3",
    "depends": ["base", "web"],
    "demo": [],
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "report_xml/static/src/js/report/action_manager_report.esm.js",
        ],
    },
}
