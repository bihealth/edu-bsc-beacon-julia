import datetime
from io import StringIO
import tempfile
import matplotlib.pyplot as plt
from pandas import DataFrame, to_datetime
from ipaddress import ip_address
from .factories import (
    RemoteSiteFactory,
    MetadataBeaconOrganizationFactory,
    LogEntryFactory,
    ConsortiumFactory,
    ProjectFactory,
    CaseFactory,
    MetadataBeaconDatasetFactory,
    MetadataBeaconFactory,
)
import sys
from django.core.management import call_command
from django.test import TestCase
from beacon.management.commands.analyse_log_entries import Command
from os import path
from unittest import mock
from django.test import Client
from django.utils import timezone


class TestAnalyseLogEntriesMethods(TestCase):
    def setUp(self):
        self.data = DataFrame(
            data={
                "method": ["GET"],
                "endpoint": ["query"],
                "remote site user": ["remote_site_1 - user_1"],
                "ip_address": [ip_address("127.0.0.1")],
                "remote site": ["remote_site_1"],
                "date_time": [to_datetime(d).tz_localize(None) for d in ["2021-05-19"]],
                "status code": [200],
                "response_size": [730],
                "reference": ["T"],
                "alternative": ["C"],
                "chromosome": ["1"],
                "start": [1],
                "end": [2],
                "release": ["GRCh37"],
                "case": [["case_1", "case_2"]],
                "project": [["project_1", "project_2"]],
            }
        )

    def test_create_data_frame(self):
        log_entry_no_remote_side = LogEntryFactory(remote_site=None)
        out = Command()._create_data_frame()
        df = DataFrame(
            data={
                "method": [log_entry_no_remote_side.method],
                "endpoint": [log_entry_no_remote_side.endpoint],
                "remote site user": ["Unknown - %s" % log_entry_no_remote_side.user_identifier],
                "ip_address": [log_entry_no_remote_side.ip_address],
                "remote site": ["Unknown"],
                "date_time": [to_datetime(log_entry_no_remote_side.date_time).tz_localize(None)],
                "status code": [log_entry_no_remote_side.status_code],
                "response_size": [700],
                "reference": [log_entry_no_remote_side.reference],
                "alternative": [log_entry_no_remote_side.alternative],
                "chromosome": [log_entry_no_remote_side.chromosome],
                "start": [log_entry_no_remote_side.start],
                "end": [log_entry_no_remote_side.end],
                "release": [log_entry_no_remote_side.release],
                "server protocol": [log_entry_no_remote_side.server_protocol],
                "case": [[]],
                "project": [[]],
            }
        )
        equal = out.equals(df)
        self.assertEqual(equal, True)

    def test_create_data_frame_date_time(self):
        log_entry_no_remote_side = LogEntryFactory(remote_site=None, date_time=to_datetime("2021-06-01", utc=True))
        out = Command()._create_data_frame(True, to_datetime("2021-06-01", utc=True), to_datetime("2021-06-01", utc=True))
        df = DataFrame(
            data={
                "method": [log_entry_no_remote_side.method],
                "endpoint": [log_entry_no_remote_side.endpoint],
                "remote site user": ["Unknown - %s" % log_entry_no_remote_side.user_identifier],
                "ip_address": [log_entry_no_remote_side.ip_address],
                "remote site": ["Unknown"],
                "date_time": [to_datetime(log_entry_no_remote_side.date_time).tz_localize(None)],
                "status code": [log_entry_no_remote_side.status_code],
                "response_size": [700],
                "reference": [log_entry_no_remote_side.reference],
                "alternative": [log_entry_no_remote_side.alternative],
                "chromosome": [log_entry_no_remote_side.chromosome],
                "start": [log_entry_no_remote_side.start],
                "end": [log_entry_no_remote_side.end],
                "release": [log_entry_no_remote_side.release],
                "server protocol": [log_entry_no_remote_side.server_protocol],
                "case": [[]],
                "project": [[]],
            }
        )
        equal = out.equals(df)
        self.assertEqual(equal, True)

    def test_plot_endpoint_per_time(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_endpoint_per_time(
            self.data, fig, ax, False, figures, file_names
        )
        self.assertEqual(ax.title.get_text(), "Number of requests per endpoint")
        self.assertEqual(figures, [fig])
        self.assertEqual(file_names, ["requests_per_endpoint.pdf"])

    def test_plot_endpoint_per_time_month_day(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_endpoint_per_time(self.data, fig, ax, True, figures, file_names)
        self.assertEqual(ax.title.get_text(), "Number of requests per endpoint")

    def test_plot_request_per_remote_site(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_requests_per_remote_site(
            self.data[self.data.endpoint == "query"]["remote site"],
            fig,
            ax,
            figures,
            file_names,
        )
        self.assertEqual(ax.title.get_text(), "Number of requests per remote site")
        self.assertEqual(figures, [fig])
        self.assertEqual(file_names, ["requests_per_remote_site.pdf"])

    def test_plot_remote_site_per_variant_container(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_remote_site_per_variant_container(
            self.data[self.data.endpoint == "query"][["remote site", "case"]],
            fig,
            ax,
            "case",
            figures,
            file_names,
        )
        self.assertEqual(
            ax.title.get_text(),
            "Number of requests per case and percentage of top remote sites",
        )
        self.assertEqual(figures, [fig])
        self.assertEqual(file_names, ["requested_cases_per_remote_site.pdf"])

    def test_plot_remote_site_per_variant_container_empty(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        self.data["case"] = [[]]
        Command()._plot_remote_site_per_variant_container(
            self.data[self.data.endpoint == "query"][["remote site", "case"]],
            fig,
            ax,
            "case",
            figures,
            file_names,
        )
        self.assertEqual(
            sys.stdout.getvalue(),
            "WARNING: No data available for plotting information about the cases.\n",
        )
        self.assertEqual(figures, [])
        self.assertEqual(file_names, [])

    def test_plot_remote_site_user_per_variant_container(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_remote_site_user_per_variant_container(
            self.data[self.data.endpoint == "query"][
                ["remote site", "case", "remote site user"]
            ],
            fig,
            ax,
            "case",
            figures,
            file_names,
        )
        self.assertEqual(
            ax.title.get_text(),
            "Number of requests per case and percentage of top users per remote site",
        )
        self.assertEqual(figures, [fig])
        self.assertEqual(file_names, ["requested_cases_per_remote_site_users.pdf"])

    def test_plot_remote_site_user_per_variant_container_empty(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        self.data["case"] = [[]]
        Command()._plot_remote_site_user_per_variant_container(
            self.data[self.data.endpoint == "query"][
                ["remote site", "case", "remote site user"]
            ],
            fig,
            ax,
            "case",
            figures,
            file_names,
        )
        self.assertEqual(
            sys.stdout.getvalue(),
            "WARNING: No data available for plotting information about the cases.\n",
        )
        self.assertEqual(figures, [])
        self.assertEqual(file_names, [])

    def test_plot_access_limit_per_remote_site(self):
        RemoteSiteFactory(name="remote_site_1")
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_access_limit_per_remote_site(
            self.data[self.data.endpoint == "query"], fig, ax, figures, file_names
        )
        self.assertEqual(
            ax.title.get_text(),
            "Number of by access limit restricted requests per remote site",
        )
        self.assertEqual(figures, [fig])
        self.assertEqual(file_names, ["Number_restricted_requests_remote_site.pdf"])

    def test_plot_access_limit_per_remote_site_empty(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_access_limit_per_remote_site(
            self.data[self.data.endpoint == "info"], fig, ax, figures, file_names
        )
        self.assertEqual(
            sys.stdout.getvalue(),
            "WARNING: No data available for plotting information about the access limits per remote site.\n",
        )
        self.assertEqual(figures, [])
        self.assertEqual(file_names, [])

    def test_plot_access_limit_per_remote_site_none(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        self.data["remote site"] = "Unknown"
        Command()._plot_access_limit_per_remote_site(
            self.data[self.data.endpoint == "query"], fig, ax, figures, file_names
        )
        self.assertEqual(
            ax.title.get_text(),
            "Number of by access limit restricted requests per remote site",
        )
        self.assertEqual(figures, [fig])
        self.assertEqual(file_names, ["Number_restricted_requests_remote_site.pdf"])

    def test_plot_table_top_requested_variants(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_table_top_requested_variants(
            self.data[
                (self.data.endpoint == "query") & (self.data["status code"] != 400)
            ][["reference", "chromosome", "start", "end", "release", "alternative"]],
            fig,
            ax,
            figures,
            file_names,
        )
        self.assertEqual(ax.title.get_text(), "Top 10 requested variants")
        self.assertEqual(figures, [fig])
        self.assertEqual(file_names, ["top_10_variants.pdf"])

    def test_plot_table_top_requested_variants_empty(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_table_top_requested_variants(
            self.data[
                (self.data.endpoint == "info") & (self.data["status code"] != 400)
            ][["reference", "chromosome", "start", "end", "release", "alternative"]],
            fig,
            ax,
            figures,
            file_names,
        )
        self.assertEqual(
            sys.stdout.getvalue(),
            "WARNING: No data available for plotting information about the top ten requested variants.\n",
        )
        self.assertEqual(figures, [])
        self.assertEqual(file_names, [])

    def test_plot_status_codes_per_time(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_status_codes_per_time(
            self.data, fig, ax, False, figures, file_names
        )
        self.assertEqual(ax.title.get_text(), "Number of status codes from requests")
        self.assertEqual(figures, [fig])
        self.assertEqual(file_names, ["status_codes_requests.pdf"])

    def test_plot_status_codes_per_time_month_day(self):
        fig, ax = plt.subplots(1)
        figures = []
        file_names = []
        Command()._plot_status_codes_per_time(
            self.data, fig, ax, True, figures, file_names
        )
        self.assertEqual(ax.title.get_text(), "Number of status codes from requests")
        self.assertEqual(figures, [fig])
        self.assertEqual(file_names, ["status_codes_requests.pdf"])


class TestAnalyseLogEntries(TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.client = Client()
        self.metadata_beacon = MetadataBeaconFactory()
        self.metadata_organization = MetadataBeaconOrganizationFactory(
            metadata_beacon=self.metadata_beacon
        )
        self.metadata_dataset = MetadataBeaconDatasetFactory(
            metadata_beacon=self.metadata_beacon
        )
        self.project = ProjectFactory()
        self.consortium = ConsortiumFactory(projects=[self.project])
        self.remote_site = RemoteSiteFactory(
            name="public", key="public", consortia=[self.consortium]
        )
        self.case = CaseFactory(project=self.project)

    def call_command(self, *args, **kwargs):
        out = StringIO()
        call_command(
            "analyse_log_entries",
            *args,
            stdout=out,
            stderr=StringIO(),
            **kwargs,
        )
        return out.getvalue()

    def test_handle_empty_db(self):
        out = self.call_command()
        self.assertEqual(out, "WARNING: No data available for the given time period.\n")

    @mock.patch('beacon.management.commands.analyse_log_entries.plt.show')
    def test_handle_time_period_month_day_no_query_data(self, mock_show):
        LogEntryFactory(date_time=datetime.datetime(2021, 10, 1, tzinfo=datetime.timezone.utc), endpoint="info")
        out = self.call_command(["--time_period", "2021-05-20", "2022-05-20"])
        self.assertEqual(
            out,
            "WARNING: No data available for plotting information about query endpoint.\nA statistical overview of the logged requests was created successfully.\n",
        )

    def test_handle_time_period_invalid(self):
        out = self.call_command(["--time_period", "g", "2021-05-20"])
        self.assertEqual(out, "ERROR: Your input format of the date_time is invalid.\n")

    @mock.patch('beacon.management.commands.analyse_log_entries.plt.show')
    @mock.patch('pandas.DataFrame.to_csv')
    def test_handle_no_path_csv(self, mock_csv, mock_show):
        p1 = ProjectFactory()
        c1 = CaseFactory(project=p1)
        LogEntryFactory(endpoint="query", remote_site=self.remote_site, cases=[c1.id])
        out = self.call_command(["--as_csv"])
        self.assertEqual(
            out,
            "WARNING: The log_entry_data.csv file was saved in the current working directory.\nA statistical overview of the logged requests was created successfully.\n",
        )

    def test_filled_path_csv(self):
        LogEntryFactory(remote_site=self.remote_site, cases=[self.case.id])
        LogEntryFactory(remote_site=self.remote_site, cases=[self.case.id])
        LogEntryFactory(remote_site=self.remote_site, cases=[self.case.id])
        with self.test_dir:
            out = self.call_command(["--path", self.test_dir.name, "--as_csv"])
            file_exist_csv = path.isfile("log_entry_data.csv")
            file_exist_request_endpoints = path.isfile("requests_per_endpoint.pdf")
            file_exist_request_remote_site = path.isfile("requests_per_remote_site.pdf")
            file_exist_case_remote_site = path.isfile("requested_cases_per_remote_site.pdf")
            file_exist_project_remote_site = path.isfile(
                "requested_projects_per_remote_site.pdf"
            )
            file_exist_case_user = path.isfile("requested_cases_per_remote_site_users.pdf")
            file_exist_project_user = path.isfile(
                "requested_projects_per_remote_site_users.pdf"
            )
            file_exist_number_restricted_requests = path.isfile(
                "Number_restricted_requests_remote_site.pdf"
            )
            file_exist_top_variants = path.isfile("top_10_variants.pdf")
            file_exist_status_codes = path.isfile("status_codes_requests.pdf")
            self.assertEqual(file_exist_csv, True)
            self.assertEqual(file_exist_request_endpoints, True)
            self.assertEqual(file_exist_request_remote_site, True)
            self.assertEqual(file_exist_case_remote_site, True)
            self.assertEqual(file_exist_project_remote_site, True)
            self.assertEqual(file_exist_case_user, True)
            self.assertEqual(file_exist_project_user, True)
            self.assertEqual(file_exist_number_restricted_requests, True)
            self.assertEqual(file_exist_top_variants, True)
            self.assertEqual(file_exist_status_codes, True)
            self.assertEqual(
                "A statistical overview of the logged requests was created successfully.\n",
                out,
            )

    @mock.patch('beacon.management.commands.analyse_log_entries.plt.show')
    @mock.patch('pandas.DataFrame.to_csv')
    def test_filled_csv_error(self, mock_to_csv, mock_show):
        file_exist = path.isfile("log_entry_data.csv")
        self.assertEqual(file_exist, False)
        p1 = ProjectFactory()
        c1 = CaseFactory(project=p1)
        LogEntryFactory(remote_site=self.remote_site, cases=[c1.id])
        mock_to_csv.side_effect = OSError('Some error was thrown')
        out = self.call_command("--as_csv")
        file_exist = path.isfile("log_entry_data.csv")
        self.assertEqual(file_exist, False)
        self.assertEqual(
            out, "ERROR: You have no writing permission for the current directory.\n"
        )

    @mock.patch('beacon.management.commands.analyse_log_entries.os.chdir')
    def test_filled_path_csv_error(self, mock_chdir):
        p1 = ProjectFactory()
        c1 = CaseFactory(project=p1)
        LogEntryFactory(remote_site=self.remote_site, cases=[c1.id])
        mock_chdir.side_effect = OSError('Some error was thrown')
        with self.test_dir:
            out = self.call_command(["--path", self.test_dir.name, "--as_csv"])
            file_exist_csv = path.isfile("log_entry_data.csv")
            file_exist_request_endpoints = path.isfile("requests_per_endpoint.pdf")
            file_exist_request_remote_site = path.isfile("requests_per_remote_site.pdf")
            file_exist_case_remote_site = path.isfile("requested_cases_per_remote_site.pdf")
            file_exist_project_remote_site = path.isfile(
                "requested_projects_per_remote_site.pdf"
            )
            file_exist_case_user = path.isfile("requested_cases_per_remote_site_user.pdf")
            file_exist_project_user = path.isfile(
                "requested_projects_per_remote_site_user.pdf"
            )
            file_exist_number_restricted_requests = path.isfile(
                "Number_restricted_requests_remote_site.pdf"
            )
            file_exist_top_variants = path.isfile("top_10_variants.pdf")
            file_exist_status_codes = path.isfile("status_codes_requests.pdf")
            self.assertEqual(file_exist_request_endpoints, False)
            self.assertEqual(file_exist_request_remote_site, False)
            self.assertEqual(file_exist_case_remote_site, False)
            self.assertEqual(file_exist_project_remote_site, False)
            self.assertEqual(file_exist_case_user, False)
            self.assertEqual(file_exist_project_user, False)
            self.assertEqual(file_exist_number_restricted_requests, False)
            self.assertEqual(file_exist_top_variants, False)
            self.assertEqual(file_exist_status_codes, False)
            self.assertEqual(file_exist_csv, False)
            self.assertEqual(
                out,
                "ERROR: Couldn't find the directory or permission for the directory is missing: %s\n"
                % str(self.test_dir.name),
            )
