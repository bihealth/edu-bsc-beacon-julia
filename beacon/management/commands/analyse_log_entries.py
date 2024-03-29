from django.core.management.base import BaseCommand
from beacon.models import LogEntry, RemoteSite
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt

#: Suppress warning for too many figures opened for testing
plt.rcParams.update({"figure.max_open_warning": 0})


class Command(BaseCommand):
    """
    Custom commands for the admin.
    """

    help = "Creates a statistical overview about the logged requests"

    def add_arguments(self, parser):
        """
        Defines the flags given to the command.

        :param parser: parser object
        """
        parser.add_argument(
            "--path", type=str, help="Given path to directory where to save the data"
        )
        parser.add_argument(
            "--as_csv",
            action="store_true",
            help="Saves data as a csv file.",
        )
        parser.add_argument(
            "--time_period",
            nargs=2,
            help="The time period to look at like '2021-05-03' '2021-10-01'.",
        )

    def handle(self, *args, **options):
        """
        Creates a statistical overview of the logged requests.

        :param args:
        :param options: Flags for optionally create a csv file "--as_csv", save plots in given directory "--path" 
         and define the to be observed time period "--time_period '2021-10-01' '2022-10-01'"
        :return: A stdout string if successful otherwise returns an error or warning.
        """
        # if argument given time period, filter for given time period
        if options["time_period"]:
            try:
                time_start = pd.to_datetime(options["time_period"][0], utc=True)
                time_end = pd.to_datetime(options["time_period"][1], utc=True)
                # checks if input is invalid
                if (
                    (time_start > time_end)
                    or pd.isnull(time_start)
                    or pd.isnull(time_end)
                ):
                    raise Exception()
            except Exception:
                return self.stdout.write(
                    self.style.ERROR(
                        "ERROR: Your input format of the date_time is invalid."
                    )
                )
            # creates dataframe for given time period
            log_data = self._create_data_frame(True, time_start, time_end)
        else:
            # creates dataframe for all logged entries
            log_data = self._create_data_frame()
        # checks whether dataframe is not empty
        if log_data.empty:
            return self.stdout.write(
                self.style.WARNING(
                    "WARNING: No data available for the given time period."
                )
            )
        # sets date time as an index for dataframe
        log_data_indexed = log_data.set_index("date_time")
        # sets style used for plotting
        plt.style.use("seaborn-bright")
        # checks whether data is just from one month
        # indicator for used daily data points in plots
        month_day = False
        if log_data_indexed.index.year.nunique() == 1:
            month_day = True
        # figures and plot names for saving them later
        figures = []
        file_names = []
        fig1, ax1 = plt.subplots(1)
        fig2, ax2 = plt.subplots(1)
        log_data_indexed.reset_index(inplace=True)
        # making plots
        self._plot_endpoint_per_time(
            log_data_indexed, fig1, ax1, figures, file_names, month_day
        )
        figures.append(fig1)
        file_names.append("requests_per_endpoint.pdf")
        self._plot_status_codes_per_time(
            log_data_indexed, fig2, ax2, figures, file_names, month_day
        )
        figures.append(fig2)
        file_names.append("status_codes_requests.pdf")
        log_data_query = log_data.loc[log_data.endpoint == "query"]
        # checks whether there are data points with query as endpoint
        if log_data_query.empty:
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: No data available for plotting information about query endpoint."
                )
            )
        else:
            # making plots
            log_data_query.reset_index(inplace=True)
            fig3, ax3 = plt.subplots(1)
            self._plot_requests_per_remote_site(
                log_data_query["remote site"], fig3, ax3, figures, file_names
            )
            figures.append(fig3)
            file_names.append("requests_per_remote_site.pdf")
            fig4, ax4 = plt.subplots(1)
            self._plot_remote_site_per_variant_container(
                log_data_query[["remote site", "case"]],
                fig4,
                ax4,
                "case",
                figures,
                file_names,
            )
            fig5, ax5 = plt.subplots(1)
            self._plot_remote_site_per_variant_container(
                log_data_query[["remote site", "project"]],
                fig5,
                ax5,
                "project",
                figures,
                file_names,
            )
            fig6, ax6 = plt.subplots(1)
            self._plot_remote_site_user_per_variant_container(
                log_data_query[["remote site user", "case", "remote site"]],
                fig6,
                ax6,
                "case",
                figures,
                file_names,
            )
            fig7, ax7 = plt.subplots(1)
            self._plot_remote_site_user_per_variant_container(
                log_data_query[["remote site user", "project", "remote site"]],
                fig7,
                ax7,
                "project",
                figures,
                file_names,
            )
            fig8, ax8 = plt.subplots(1)
            self._plot_access_limit_per_remote_site(
                log_data_query, fig8, ax8, figures, file_names
            )
            fig9, ax9 = plt.subplots(1)
            self._plot_table_top_requested_variants(
                log_data_query[log_data_query["status code"] != 400][
                    [
                        "reference",
                        "chromosome",
                        "start",
                        "end",
                        "release",
                        "alternative",
                    ]
                ],
                fig9,
                ax9,
                figures,
                file_names,
            )
        # checks if '--path' argument was passed
        if options["path"]:
            path = options["path"]
            # trying to save plot files
            try:
                os.chdir(path)
                for figure, file_name in zip(figures, file_names):
                    figure.savefig(file_name)
                # if argument '--as_csv' was passed save data as csv file
                if options["as_csv"]:
                    log_data.to_csv("log_entry_data.csv")
            except OSError:
                return self.stdout.write(
                    self.style.ERROR(
                        "ERROR: Couldn't find the directory or permission for the directory is missing: %s"
                        % str(path)
                    )
                )
        else:
            # shows all the plots
            plt.show()
            # if argument '--as_csv' was passed save csv file in current directory
            if options["as_csv"]:
                try:
                    log_data.to_csv("log_entry_data.csv")
                    self.stdout.write(
                        self.style.WARNING(
                            "WARNING: The log_entry_data.csv file was saved in the current working directory."
                        )
                    )
                except OSError:
                    return self.stdout.write(
                        self.style.ERROR(
                            "ERROR: You have no writing permission for the current directory."
                        )
                    )
        return self.stdout.write(
            self.style.SUCCESS(
                "A statistical overview of the logged requests was created successfully."
            )
        )

    # logs = pandas.DataFrame(LogEntry.objects.all().values())
    def _create_data_frame(self, time_period=False, time_start=None, time_end=None):
        """
        Creates a pandas DataFrame object by querying the database for the the LogEntry entries
        and filters entries optionally for a given time period.

        :param time_period: bool indicating if time period is given
        :param time_start: a pandas datetime object
        :param time_end: a pandas datetime object
        :return: a pandas DataFrame object containing the LogEntry data
        """
        methods = []
        endpoints = []
        user_identifiers = []
        ip_addresses = []
        remote_sites_names = []
        date_times = []
        status_codes = []
        response_sizes = []
        references = []
        alternatives = []
        chromosomes = []
        starts = []
        ends = []
        releases = []
        server_protocols = []
        cases = []
        projects = []
        # in case time period is given filters LogEntry entries
        if time_period:
            log_entries = LogEntry.objects.filter(
                date_time__gte=time_start, date_time__lte=time_end
            )
        # query database for all LogEntry entries
        else:
            log_entries = LogEntry.objects.all()
        # read data from 'log_entries' QuerySet
        for log in log_entries:
            cases_query_set = log.cases.all()
            cases.append([c.name for c in cases_query_set])
            projects.append([c.project.title for c in cases_query_set])
            methods.append(log.method)
            endpoints.append(log.endpoint)
            ip_addresses.append(log.ip_address)
            if log.remote_site is None:
                remote_sites_names.append("Unknown")
            else:
                remote_sites_names.append(
                    RemoteSite.objects.get(id=log.remote_site.id).name
                )
            user_identifiers.append(
                "%s - %s"
                % (remote_sites_names[len(remote_sites_names) - 1], log.user_identifier)
            )
            date_times.append(log.date_time)
            status_codes.append(log.status_code)
            response_sizes.append(log.response_size)
            references.append(log.reference)
            alternatives.append(log.alternative)
            chromosomes.append(log.chromosome)
            starts.append(log.start)
            ends.append(log.end)
            releases.append(log.release)
            server_protocols.append(log.server_protocol)
        return pd.DataFrame(
            data={
                "method": methods,
                "endpoint": endpoints,
                "remote site user": user_identifiers,
                "ip_address": ip_addresses,
                "remote site": remote_sites_names,
                # time zone removed
                "date_time": [pd.to_datetime(d).tz_localize(None) for d in date_times],
                "status code": status_codes,
                "response_size": response_sizes,
                "reference": references,
                "alternative": alternatives,
                "chromosome": chromosomes,
                "start": starts,
                "end": ends,
                "release": releases,
                "server protocol": server_protocols,
                "case": cases,
                "project": projects,
            }
        )

    def _plot_endpoint_per_time(
        self, data, fig, ax, figures, file_names, month_day=False
    ):
        """
        Creates a plot containing information about the number of request per endpoint and
        per time scaled per month or per year depending on the month_day input. Appends
        the created plot to the figures and its name to file names.

        :param data: pandas DataFrame object
        :param fig: matplotlib figure object
        :param ax: matplotlib ax
        :param figures: list of matplotlib figures objects
        :param file_names: list of strings
        :param month_day: bool True if the data contains just data for one month, default is False
        """
        # creates new dataframe for plotting
        endpoints_df = pd.DataFrame(data={})
        # add column to dataframe for each endpoint
        for endpoint in data["endpoint"].unique():
            endpoints_df[endpoint] = [int(d) for d in data["endpoint"] == endpoint]
        # adds date_time as column
        endpoints_df["date_time"] = data["date_time"]
        # set datetime index
        endpoints_df = endpoints_df.set_index("date_time")
        # if True uses daily data points for plotting
        if month_day:
            endpoints_df.groupby(
                [
                    endpoints_df.index.year,
                    endpoints_df.index.month,
                    endpoints_df.index.day,
                ]
            ).sum().plot(
                kind="line",
                style=".-",
                ax=ax,
                ylabel="Number of requests",
                xlabel="Time period (year, month, day)",
            )
        else:
            endpoints_df.groupby(
                [endpoints_df.index.year, endpoints_df.index.month]
            ).sum().plot(
                kind="line",
                style=".-",
                ax=ax,
                ylabel="Number of requests",
                xlabel="Time period (year, month)",
            )
        ax.set_title("Number of requests per endpoint")
        ax.tick_params("x", labelrotation=350)
        figures.append(fig)
        file_names.append("requests_per_endpoint.pdf")

    def _plot_status_codes_per_time(
        self, data, fig, ax, figures, file_names, month_day=False
    ):
        """
        Creates a plot containing information about the number of request having a certain status
        code per time scaled per month or per year depending on the month_day input. Appends
        the created plot to the figures and its name to file names.

        :param data: pandas DataFrame object
        :param fig: matplotlib figure object
        :param ax: matplotlib ax
        :param figures: list of matplotlib figures objects
        :param file_names: list of strings
        :param month_day: bool True if the data contains just data for one month, default is False
        """
        # creates new dataframe for plotting
        status_codes_df = pd.DataFrame(data={})
        # add column to dataframe for each status code
        for status in data["status code"].unique():
            status_codes_df[status] = [int(d) for d in data["status code"] == status]
        # adds date_time as column
        status_codes_df["date_time"] = data["date_time"]
        # set datetime index
        status_codes_df = status_codes_df.set_index("date_time")
        # if True uses daily data points for plotting
        if month_day:
            status_codes_df.groupby(
                [
                    status_codes_df.index.year,
                    status_codes_df.index.month,
                    status_codes_df.index.day,
                ]
            ).sum().plot(
                kind="line",
                style=".-",
                ax=ax,
                ylabel="Number of requests",
                xlabel="Time period (year, month, day)",
            )
        else:
            status_codes_df.groupby(
                [status_codes_df.index.year, status_codes_df.index.month]
            ).sum().plot(
                kind="line",
                style=".-",
                ax=ax,
                ylabel="Number of requests",
                xlabel="Time period (year, month)",
            )
        ax.tick_params("x", labelrotation=350)
        ax.set_title("Number of status codes from requests")
        figures.append(fig)
        file_names.append("status_codes_requests.pdf")

    def _plot_requests_per_remote_site(self, data, fig, ax, figures, file_names):
        """
        Creates a plot containing information about the number of request per remote site.
        Appends the created plot to the figures and its name to file names.

        :param data: pandas DataFrame object
        :param fig: matplotlib figure object
        :param ax: matplotlib ax
        :param figures: list of matplotlib figures objects
        :param file_names: list of strings
        """
        # counts requests per remote site
        data.value_counts().head(15).plot(
            kind="bar", ax=ax, ylabel="Number of requests", xlabel="Remote site"
        )
        ax.set_title("Number of requests per remote site")
        ax.tick_params("x", labelrotation=350)
        figures.append(fig)
        file_names.append("requests_per_remote_site.pdf")

    def _plot_remote_site_per_variant_container(
        self, data, fig, ax, variant_container, figures, file_names
    ):
        """
        Creates a plot containing information about the number of request
        per variant container (either case or project), mayor requesting
        remote site of each variant container and the proportion of it on
        the number of request in percentage. Appends the created plot to
        the figures and its name to file names.

        :param data: pandas DataFrame object
        :param fig: matplotlib figure object
        :param ax: matplotlib ax
        :param variant_container: string
        :param figures: list of matplotlib figures objects
        :param file_names: list of strings
        """
        # read in data
        remote_sites = []
        variant_containers = []
        for i in range(0, len(data[variant_container])):
            for var_container in data[variant_container][i]:
                variant_containers.append(var_container)
                remote_sites.append(data["remote site"].loc[i])
        case_project_data = pd.DataFrame(
            {
                "remote site": remote_sites,
                variant_container: variant_containers,
            }
        )
        if variant_containers:
            # count data points per remote site
            table_count_remote_site = case_project_data.pivot_table(
                index=variant_container, columns="remote site", aggfunc="size"
            )
            # get maximum counted remote site and percentage
            max_remote_site = [
                table_count_remote_site.columns[
                    np.argmax(
                        table_count_remote_site[
                            table_count_remote_site.index == c
                        ].max()
                    )
                ]
                for c in table_count_remote_site.index
            ]
            max_percentage = sorted(
                [
                    round(
                        table_count_remote_site[table_count_remote_site.index == c]
                        .max()
                        .max()
                        / sum(
                            table_count_remote_site[
                                table_count_remote_site.index == c
                            ].sum()
                        ),
                        2,
                    )
                    for c in table_count_remote_site.index
                ],
                reverse=True,
            )
            # get total counts
            total_call_counts = case_project_data.pivot_table(
                index=variant_container, aggfunc="size"
            )
            # create pivot table for plotting values
            table = pd.DataFrame(
                {
                    "total_call_count": total_call_counts,
                    "Maximal requesting identifier": max_remote_site,
                }
            )
            # sort values and plot top 15
            table.sort_values("total_call_count", ascending=False).pivot_table(
                index=table.index,
                columns="Maximal requesting identifier",
                values="total_call_count",
            ).head(15).plot(
                kind="bar",
                stacked=True,
                ax=ax,
                ylabel="Number of requests",
                xlabel=(
                    "%s%ss" % (variant_container[0].upper(), variant_container[1:])
                ),
            )
            # add percentage per most often requesting identifier
            rects = ax.patches
            for rect, label, height in zip(
                rects,
                [("%s%s" % (round(mp * 100,2), "%")) for mp in max_percentage[:15]],
                sorted(total_call_counts, reverse=True)[:15],
            ):
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    height,
                    label,
                    ha="center",
                    va="bottom",
                )
            ax.tick_params("x", labelrotation=350)
            ax.set_title(
                "Number of requests per %s and percentage of top remote sites"
                % variant_container
            )
            figures.append(fig)
            file_names.append("requested_%ss_per_remote_site.pdf" % variant_container)
        else:
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: No data available for plotting information about the %ss."
                    % variant_container
                )
            )

    def _plot_remote_site_user_per_variant_container(
        self, data, fig, ax, variant_container, figures, file_names
    ):
        """
        Creates a plot containing information about the number of request
        per variant container (either case or project), mayor requesting
        remote site and its mayor requesting user of each variant container
        and the users proportion per remote site of the number of request in
        percentage. Appends the created plot to the figures and its name to
        file names.

        :param data: pandas DataFrame object
        :param fig: matplotlib figure object
        :param ax: matplotlib ax
        :param variant_container: string
        :param figures: list of matplotlib figures objects
        :param file_names: list of strings
        """
        # read in data
        remote_sites = []
        variant_containers = []
        users = []
        for i in range(0, len(data[variant_container])):
            for var_container in data[variant_container][i]:
                variant_containers.append(var_container)
                remote_sites.append(data["remote site"].loc[i])
                users.append(data["remote site user"].loc[i])
        case_project_data = pd.DataFrame(
            {
                "remote site": remote_sites,
                variant_container: variant_containers,
                "remote site user": users,
            }
        )
        if variant_containers:
            # count per remote site
            table_count_remote_site = case_project_data.pivot_table(
                index=variant_container, columns="remote site", aggfunc="size"
            )
            # get maximum count identifier
            max_remote_site = [
                table_count_remote_site.columns[
                    np.argmax(
                        table_count_remote_site[
                            table_count_remote_site.index == c
                        ].max()
                    )
                ]
                for c in table_count_remote_site.index
            ]
            # get total counts
            total_call_counts = case_project_data.pivot_table(
                index=variant_container, aggfunc="size"
            )
            # get counts user per remote site
            table_count_user = case_project_data.pivot_table(
                index=[variant_container, "remote site"],
                columns="remote site user",
                aggfunc="size",
            )
            # get max requesting user per remote site and percentage
            max_user = [
                table_count_user.columns[
                    table_count_user.loc[(case, remote_site)].argmax().max()
                ]
                for case, remote_site in zip(total_call_counts.index, max_remote_site)
            ]
            max_percentage = sorted(
                [
                    round(
                        table_count_user.loc[(case, remote_site)].max()
                        / table_count_user.loc[(case, remote_site)].sum(),
                        2,
                    )
                    for case, remote_site in zip(
                        total_call_counts.index, max_remote_site
                    )
                ],
                reverse=True,
            )
            # create pivot table for plotting
            table = pd.DataFrame(
                {
                    "total_call_count": total_call_counts,
                    "Maximal requesting user per remote site": max_user,
                }
            )
            # sort table and plot top 15
            table.sort_values("total_call_count", ascending=False).pivot_table(
                index=table.index,
                columns="Maximal requesting user per remote site",
                values="total_call_count",
            ).head(15).plot(
                kind="bar",
                stacked=True,
                ax=ax,
                ylabel="Number of requests",
                xlabel=(
                    "%s%ss" % (variant_container[0].upper(), variant_container[1:])
                ),
            )
            # add percentage per most often requesting user per remote site
            rects = ax.patches
            for rect, label, height in zip(
                rects,
                [("%s%s" % (round(mp * 100, 2), "%")) for mp in max_percentage[:15]],
                sorted(total_call_counts, reverse=True)[:15],
            ):
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    height,
                    label,
                    ha="center",
                    va="bottom",
                )
            ax.tick_params("x", labelrotation=350)
            ax.set_title(
                "Number of requests per %s and percentage of top users per remote site"
                % variant_container
            )
            figures.append(fig)
            file_names.append(
                "requested_%ss_per_remote_site_users.pdf" % variant_container
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: No data available for plotting information about the %ss."
                    % variant_container
                )
            )

    def _plot_access_limit_per_remote_site(self, data, fig, ax, figures, file_names):
        """
        Creates a plot containing information about the number of request per remote site
        comparing status codes indicating how often a remote site tries to exceed its
        access limits. Appends the created plot to the figures and its name to file names.

        :param data: pandas DataFrame object
        :param fig: matplotlib figure object
        :param ax: matplotlib ax
        :param figures: list of matplotlib figures objects
        :param file_names: list of strings
        """
        df_idx_remote_sites = data[data["status code"].isin([200, 403])].set_index(
            "remote site"
        )
        if df_idx_remote_sites.empty:
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: No data available for plotting information about the access limits per remote site."
                )
            )
        else:
            df_idx_remote_sites.groupby(
                [df_idx_remote_sites.index, "status code"]
            ).size().head(15).unstack().plot(
                kind="bar",
                ax=ax,
                ylabel="Number of requests",
                xlabel="Remote site, Access limit",
            )
            # label each remote site with corresponding access limit
            xtick_labels = []
            for label in ax.get_xticklabels():
                label_text = label.get_text()
                remote_site = RemoteSite.objects.filter(name=label_text).first()
                if not remote_site:
                    access_limit = None
                else:
                    access_limit = remote_site.access_limit
                xtick_labels.append("%s, %s" % (label_text, access_limit))
            ax.set_xticklabels(xtick_labels)
            ax.tick_params("x", labelrotation=350)
            ax.set_title(
                "Number of by access limit restricted requests per remote site"
            )
            figures.append(fig)
            file_names.append("Number_restricted_requests_remote_site.pdf")

    def _plot_table_top_requested_variants(self, data, fig, ax, figures, file_names):
        """
        Creates a plot containing a table with the top ten requested variants.
        Appends the created plot to the figures and its name to file names.

        :param data: pandas DataFrame object
        :param fig: matplotlib figure object
        :param ax: matplotlib ax
        :param figures: list of matplotlib figures objects
        :param file_names: list of strings
        """
        data["request number"] = np.zeros(data.shape[0], np.int8)
        # create table for plotting
        df_table = (
            data.groupby(
                ["chromosome", "start", "end", "reference", "alternative", "release"],
                as_index=False,
            )
            .agg({"request number": pd.Series.count})
            .sort_values("request number", ascending=False)
        )
        if df_table.empty:
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: No data available for plotting information about the top ten requested variants."
                )
            )
        else:
            # plot table
            table = pd.plotting.table(
                ax=ax,
                data=df_table[:10],
                colLabels=df_table.columns,
                rowLabels=None,
                loc="center",
                colColours=["gainsboro"] * 7,
            )
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.auto_set_column_width(col=list(range(len(df_table.columns))))
            ax.set_title("Top 10 requested variants")
            ax.axis("off")
            figures.append(fig)
            file_names.append("top_10_variants.pdf")
