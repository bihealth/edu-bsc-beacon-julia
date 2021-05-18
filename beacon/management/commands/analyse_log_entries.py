from django.core.management.base import BaseCommand
from beacon.models import LogEntry, RemoteSite
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt


class Command(BaseCommand):
    """
    Custom commands for the admin.
    """
    help = 'Creates a statistical overview about the logged requests'

    def add_arguments(self, parser):
        """
        Defines the flags given to the command.

        :param parser: parser object
        """
        parser.add_argument('--path', type=str, help="Given path to directory where to save the data")
        parser.add_argument(
            '--as_csv',
            action='store_true',
            help='Saves data as a csv file.',
        )
        parser.add_argument(
            '--time_period',
            nargs=2,
            help="The time period to look at like '2021-05-03' '2021-10-01'.",
        )

    def handle(self, *args, **options):
        """
        Creates a statistical overview of the logged requests.

        :param args:
        :param options: Flags for optional create csv file, save plots in given directory
        and define to be observed time period
        :return: A stdout string if successful otherwise returns an error.
        """
        plt.style.use('seaborn-bright')
        if options["path"]:
            path = options["path"]
            try:
                os.chdir(path)
            except OSError:
                return self.stderr.write(
                    self.style.ERROR("Couldn't find the directory or permission for the directory is missing: " + path))
        methods = []
        endpoints = []
        user_identifiers = []
        ip_addresses = []
        authuser_names = []
        date_times = []
        status_codes = []
        response_sizes = []
        references = []
        alternatives = []
        chromosomes = []
        starts = []
        ends = []
        releases = []
        cases = []
        projects = []
        for l in LogEntry.objects.all()[len(LogEntry.objects.all()) - 13:]:  # TODO: all again
            cases_query_set = l.cases.all()
            cases.append([c.name for c in cases_query_set])
            projects.append([c.project.title for c in cases_query_set])
            method, endpoint, reference, alternative, chromosome, start, end, release = self._read_in_request(
                l.request)
            methods.append(method)
            endpoints.append(endpoint)
            ip_addresses.append(l.ip_address)
            if l.authuser_id is None:
                authuser_names.append("Unknown")
            else:
                authuser_names.append(RemoteSite.objects.get(id=l.authuser_id).name)
            user_identifiers.append("%s - %s" % (authuser_names[len(authuser_names)-1], l.user_identifier)) #TODO: rethink
            date_times.append(l.date_time)
            status_codes.append(l.status_code)
            response_sizes.append(l.response_size)
            references.append(reference)
            alternatives.append(alternative)
            chromosomes.append(chromosome)
            starts.append(start)
            ends.append(end)
            releases.append(release)
        #TODO: None values to "None"?
        log_data = pd.DataFrame(data={"method": methods,
                                      "endpoint": endpoints,
                                      # TODO: check can user identifier be None?
                                      "user_identifier": user_identifiers,
                                      "ip_address": ip_addresses,
                                      "authuser_name": authuser_names,
                                      # time zone removed
                                      "date_time": [pd.to_datetime(d).tz_localize(None) for d in date_times],
                                      # Just None for invalid input or info endpoint
                                      "status_code": status_codes,
                                      "response_size": response_sizes,
                                      "reference": references,
                                      "alternative": alternatives,
                                      "chromosome": chromosomes,
                                      "start": starts,
                                      "end": ends,
                                      "release": releases,
                                      "case": cases,
                                      "project": projects,
                                      })
        if options["as_csv"]:
            log_data.to_csv("log_entry_data.csv")
        log_data_indexed = log_data.set_index("date_time")
        if options["time_period"]:
            try:
                time_start = pd.to_datetime(options["time_period"][0])
                time_end = pd.to_datetime(options["time_period"][1])
                if time_start > time_end:
                    raise Exception
                #TODO: if just one month set index to month - day
            except Exception:
                return self.stderr.write(self.style.ERROR("Your input format of the date_time is invalid."))
            log_data_indexed = log_data_indexed.loc[time_start:time_end]
            if log_data_indexed.empty:
                return self.stdout.write(self.style.WARNING("WARNING: No data available for the given time period."))
        #fig, ((ax1, ax2), (ax3, ax4), (ax5, ax6), (ax7, ax8), (ax9, ax10)) = plt.subplots(5, 2)
        plt.figure() # TODO: headlines for all plots, label="Number of request per endpoint"
        grid = plt.GridSpec(3, 3, wspace=0.1, hspace=0.8)
        ax1 = plt.subplot(grid[0, 0])
        ax2 = plt.subplot(grid[0, 1])
        ax3 = plt.subplot(grid[0, 2])
        ax4 = plt.subplot(grid[1, 0])
        ax5 = plt.subplot(grid[1, 1])
        ax6 = plt.subplot(grid[1, 2])
        ax7 = plt.subplot(grid[2, 0])
        ax9 = plt.subplot(grid[2, 1])
        ax8 = plt.subplot(grid[2, 2])
        self._plot_endpoint_per_time(log_data_indexed, ax1)
        log_data_query = log_data_indexed.loc[log_data_indexed.endpoint == 'query']
        log_data_query.reset_index(level=0, inplace=True)
        self._plot_requests_per_authuser(log_data_query["authuser_name"], ax2)
        self._plot_identifier_per_variant_container(log_data_query[["authuser_name", "case"]], ax3, 'authuser_name', 'case')
        self._plot_identifier_per_variant_container(log_data_query[["authuser_name", "project"]], ax4, 'authuser_name', 'project')
        self._plot_identifier_per_variant_container(log_data_query[["user_identifier", "case"]], ax5, 'user_identifier', 'case')
        self._plot_identifier_per_variant_container(log_data_query[["user_identifier", "project"]], ax6, 'user_identifier', 'project')
        self._plot_access_limit_per_authuser(log_data_query, ax7)
        self._plot_table_top_requested_variants(log_data_query[log_data_query.status_code != 400], ax8)
        self._plot_status_codes_per_time(log_data_indexed, ax9)
        if options["path"]:
            plt.savefig("calls_per_endpoint.pdf")
            if options["as_csv"]:
                try:
                    log_data.to_csv("log_entry_data.csv")
                except OSError:
                    return self.stderr.write(
                        self.style.ERROR("You have no writing permission for the current directory."))
        else:
            plt.show()
            if options["as_csv"]:
                try:
                    log_data.to_csv("log_entry_data.csv")
                    self.stdout.write(self.style.WARNING(
                        "WARNING: The log_entry_data.csv file was saved in the current working directory."))
                except OSError:
                    return self.stderr.write(
                        self.style.ERROR("You have no writing permission for the current directory."))
        return self.stdout.write(
            self.style.SUCCESS("A statistical overview of the logged requests was created successfully."))

    def _read_in_request(self, request_field):
        """
        Reads the request string data containing the method, query string dictionary and the server protocol.

        :param request_field: string of request of LogEntry object
        :return: a string for the method, the endpoint, the reference base, the alternative base, the chromosome,
        the start position, the end position, the release
        """
        request_info_list = request_field.split(";")
        method = request_info_list[0]
        endpoint = request_info_list[1]
        if endpoint == '/query':
            if str([]) == request_info_list[2]:
                return method, "query", None, None, None, None, None, None
            else:
                query_list = request_info_list[2].split('(')
                var_dict = {}
                last = len(query_list)
                for q in query_list[1:last - 1]:
                    k = q[:len(q) - 2].split(",")[0]
                    v = q[:len(q) - 3].split(",")[1]
                    var_dict[k[1:len(k) - 1]] = v[2:len(v) - 1]
                k = query_list[last - 1][:len(query_list[last - 1]) - 2].split(",")[0]
                v = query_list[last - 1][:len(query_list[last - 1]) - 3].split(",")[1]
                var_dict[k[1:len(k) - 1]] = v[2:len(v)]
                if 'referenceBases' in var_dict.keys():
                    reference = var_dict['referenceBases']
                else:
                    reference = None
                if 'alternateBases' in var_dict.keys():
                    alternative = var_dict['alternateBases']
                else:
                    alternative = None
                if 'referenceName' in var_dict.keys():
                    chromosome = var_dict['referenceName']
                else:
                    chromosome = None
                if 'start' in var_dict.keys():
                    start = int(var_dict["start"])
                else:
                    start = None
                if 'end' in var_dict.keys():
                    end = int(var_dict["end"])
                else:
                    end = None
                if 'assemblyId' in var_dict.keys():
                    release = var_dict['assemblyId']
                else:
                    release = "GRCh37"
                return method, "query", reference, alternative, chromosome, start, end, release
        else:
            return method, "info", None, None, None, None, None, None

    def _plot_endpoint_per_time(self, data, ax):
        data.groupby([data.index.year, data.index.month, "endpoint"]).size().unstack().plot(kind='line', ax=ax, ylabel="Number of requests", xlabel="Time period")

    def _plot_requests_per_authuser(self, data, ax):
        data.value_counts().plot(kind='bar', ax=ax, ylabel="Number of requests", xlabel="Authuser")

    def _plot_identifier_per_variant_container(self, data, ax, identifier, variant_container):
        identifiers = []
        variant_containers = []
        for i in range(1, len(data[variant_container])):
            for var_container in data[variant_container][i]:
                variant_containers.append(var_container)
                identifiers.append(identifier)
        case_project_data = pd.DataFrame({identifier: identifiers,
                                          variant_container: variant_containers,
                                          })
        # count per authuser
        table = case_project_data.pivot_table(index=variant_container, columns=identifier, aggfunc='size')
        # get maximum count authuser and percentage
        max_authuser = [table.columns[np.argmax(table[table.index == c].max())] for c in table.index]
        max_percentage = sorted([round(table[table.index == c].max().max() / sum(table[table.index == c].sum()), 2) for c in table.index], reverse=True)
        # count total
        total = case_project_data.pivot_table(index=variant_container, aggfunc='size')
        table["max_authuser"] = max_authuser
        table = pd.DataFrame({"total": total, "max_authuser": max_authuser})
        head_number = int(np.ceil(len(total) * 0.1))
        table.sort_values('total', ascending=False).pivot_table(index=table.index, columns="max_authuser",
                                                                values="total").head(head_number).plot(kind='bar',
                                                                                                       stacked=True,
                                                                                                       ax=ax)
        rects = ax.patches
        for rect, label, height in zip(rects, max_percentage[:head_number], sorted(total, reverse=True)[:head_number]):
            ax.text(rect.get_x() + rect.get_width() / 2, height + 1, label,
                    ha='center', va='bottom')

    def _plot_access_limit_per_authuser(self, data, ax):
        df_idx_authuser = data[data["status_code"].isin([200, 403])].set_index("authuser_name")
        df_idx_authuser.groupby([df_idx_authuser.index, "status_code"]).size().unstack().plot(kind='bar', ax=ax, ylabel="Number of requests", xlabel="Authuser, Access Limit")
        #ax.set_xticklabels(["%s, %d" % (d.get_text(), 3) for d in plt.xticks()[1]]) #TODO get acces_limit

    def _plot_table_top_requested_variants(self, data, ax):
        df_table = pd.DataFrame({"reference": data["reference"], "chromosome": data["chromosome"], "start": data["start"], "end": data["end"], "release": data["release"], "alternative": data["alternative"], "counts": np.zeros(len(data))}).groupby(["reference", "chromosome", "start", "end", "release", "alternative"], as_index=False).agg({'counts': pd.Series.nunique}).sort_values("counts")
        pd.plotting.table(ax=ax, data=df_table[:10], colLabels=df_table.columns, rowLabels=None, loc='center', colColours=['gainsboro']*7)
        ax.axis("off")

    def _plot_status_codes_per_time(self, data, ax):
        data.groupby([data.index.year, data.index.month, "status_code"]).size().unstack().plot(kind='bar', ax=ax, ylabel="Number of requests", xlabel="Time period")
