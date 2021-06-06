from django.core.management.base import BaseCommand
from beacon.models import LogEntry, RemoteSite
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
plt.rcParams.update({'figure.max_open_warning': 0})


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
        :param options: Flags for optionally create a csv file "--as_csv", save plots in given directory "--path path"
        and define the to be observed time period "--time_period '2021-10-01' '2022-10-01'"
        :return: A stdout string if successful otherwise returns an error or warning.
        """
        log_data = self._create_data_frame()
        log_data_indexed = log_data.set_index("date_time")
        if options["time_period"]:
            try:
                time_start = pd.to_datetime(options["time_period"][0])
                time_end = pd.to_datetime(options["time_period"][1])
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
            if log_data_indexed.empty is False:
                mask = (log_data_indexed.index > time_start) & (
                    log_data_indexed.index <= time_end
                )
                log_data_indexed = log_data_indexed.loc[mask]
        if log_data_indexed.empty:
            return self.stdout.write(
                self.style.WARNING(
                    "WARNING: No data available for the given time period."
                )
            )
        plt.style.use("seaborn-bright")
        month_day = False
        if log_data_indexed.index.year.nunique() is 1:
            month_day = True
        figures = []
        file_names = []
        fig1, ax1 = plt.subplots(1)
        fig2, ax2 = plt.subplots(1)
        log_data_indexed.reset_index(inplace=True)
        self._plot_endpoint_per_time(
            log_data_indexed, fig1, ax1, month_day, figures, file_names
        )
        figures.append(fig1)
        file_names.append("requests_per_endpoint.pdf")
        self._plot_status_codes_per_time(
            log_data_indexed, fig2, ax2, month_day, figures, file_names
        )
        figures.append(fig2)
        file_names.append("status_codes_requests.pdf")
        log_data_query = log_data.loc[log_data.endpoint == "query"]
        if not log_data_query.empty:
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
        else:
            self.stdout.write(
                self.style.WARNING(
                    "WARNING: No data available for plotting information about query endpoint."
                )
            )
        if options["path"]:
            path = options["path"]
            try:
                os.chdir(path)
                for figure, file_name in zip(figures, file_names):
                    figure.savefig(file_name)
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
            plt.show()
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

    def _create_data_frame(self):
        """

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
        for l in LogEntry.objects.all():
            cases_query_set = l.cases.all()
            cases.append([c.name for c in cases_query_set])
            projects.append([c.project.title for c in cases_query_set])
            methods.append(l.method)
            endpoints.append(l.endpoint)
            ip_addresses.append(l.ip_address)
            if l.remote_site is None:
                remote_sites_names.append("Unknown")
            else:
                remote_sites_names.append(RemoteSite.objects.get(id=l.remote_site.id).name)
            user_identifiers.append(
                "%s - %s" % (remote_sites_names[len(remote_sites_names) - 1], l.user_identifier)
            )
            date_times.append(l.date_time)
            status_codes.append(l.status_code)
            response_sizes.append(l.response_size)
            references.append(l.reference)
            alternatives.append(l.alternative)
            chromosomes.append(l.chromosome)
            starts.append(l.start)
            ends.append(l.end)
            releases.append(l.release)
            server_protocols.append(l.server_protocol)
        return pd.DataFrame(
            data={
                "method": methods,
                "endpoint": endpoints,
                "remote site user": user_identifiers,
                "ip_address": ip_addresses,
                "remote site": remote_sites_names,
                # time zone removed
                "date_time": [pd.to_datetime(d).tz_localize(None) for d in date_times],
                # Just None for invalid input or info endpoint
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

    def _plot_endpoint_per_time(self, data, fig, ax, month_day, figures, file_names):
        """
        Creates a plot containing information about the number of request per endpoint and
        per time scaled per month or per year depending on the month_day input. Appends
        the created plot to the figures and its name to file names.

        :param data: pandas DataFrame object
        :param fig: matplotlib figure object
        :param ax: matplotlib ax
        :param month_day: bool True if the data contains just data for one month
        :param figures: list of matplotlib figures objects
        :param file_names: list of strings
        """
        endpoints_df = pd.DataFrame(data={})
        for endpoint in data["endpoint"].unique():
            endpoints_df[endpoint] = [int(d) for d in data["endpoint"] == endpoint]
        endpoints_df["date_time"] = data["date_time"]
        endpoints_df = endpoints_df.set_index("date_time")
        if month_day:
            endpoints_df.groupby([endpoints_df.index.year, endpoints_df.index.month, endpoints_df.index.day]).sum().plot(
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
        ax.tick_params("x", labelrotation=360)
        figures.append(fig)
        file_names.append("requests_per_endpoint.pdf")

    def _plot_status_codes_per_time(
        self, data, fig, ax, month_day, figures, file_names
    ):
        """
        Creates a plot containing information about the number of request having a certain status
        code per time scaled per month or per year depending on the month_day input. Appends
        the created plot to the figures and its name to file names.

        :param data: pandas DataFrame object
        :param fig: matplotlib figure object
        :param ax: matplotlib ax
        :param month_day: bool True if the data contains just data for one month
        :param figures: list of matplotlib figures objects
        :param file_names: list of strings
        """
        status_codes_df = pd.DataFrame(data={})
        for status in data["status code"].unique():
            status_codes_df[status] = [int(d) for d in data["status code"] == status]
        status_codes_df["date_time"] = data["date_time"]
        status_codes_df = status_codes_df.set_index("date_time")
        if month_day:
            status_codes_df.groupby([status_codes_df.index.year, status_codes_df.index.month, status_codes_df.index.day]).sum().plot(
                kind="line",
                style=".-",
                ax=ax,
                ylabel="Number of requests",
                xlabel="Time period (year, month, day)",
            )
        else:
            status_codes_df.groupby(
                [status_codes_df.index.year, status_codes_df.index.month]
            ).size().unstack().plot(
                kind="line",
                style=".-",
                ax=ax,
                ylabel="Number of requests",
                xlabel="Time period (year, month)",
            )
        ax.tick_params("x", labelrotation=360)
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
        data.value_counts().head(15).plot(
            kind="bar", ax=ax, ylabel="Number of requests", xlabel="Remote site"
        )
        ax.set_title("Number of requests per remote site")
        ax.tick_params("x", labelrotation=360)
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
            # count per identifier
            table_count_remote_site = case_project_data.pivot_table(
                index=variant_container, columns="remote site", aggfunc="size"
            )
            # get maximum count identifier and percentage
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
            # create pivot table ofr plotting values
            table = pd.DataFrame(
                {
                    "total_call_count": total_call_counts,
                    "Maximal requesting identifier": max_remote_site,
                }
            )
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
                [("%s%s" % (mp * 100, "%")) for mp in max_percentage[:15]],
                sorted(total_call_counts, reverse=True)[:15],
            ):
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    height,
                    label,
                    ha="center",
                    va="bottom",
                )
            ax.tick_params("x", labelrotation=360)
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
            # count per identifier
            table_count_remote_site = case_project_data.pivot_table(
                index=variant_container, columns="remote site", aggfunc="size"
            )
            # get maximum count identifier and percentage
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
            table_count_user = case_project_data.pivot_table(
                index=[variant_container, "remote site"],
                columns="remote site user",
                aggfunc="size",
            )
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
            table = pd.DataFrame(
                {
                    "total_call_count": total_call_counts,
                    "Maximal requesting user per remote site": max_user,
                }
            )
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
            # add percentage per most often requesting identifier
            rects = ax.patches
            for rect, label, height in zip(
                rects,
                [("%s%s" % (mp * 100, "%")) for mp in max_percentage[:15]],
                sorted(total_call_counts, reverse=True)[:15],
            ):
                ax.text(
                    rect.get_x() + rect.get_width() / 2,
                    height,
                    label,
                    ha="center",
                    va="bottom",
                )
            ax.tick_params("x", labelrotation=360)
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
            df_idx_remote_sites.groupby([df_idx_remote_sites.index, "status code"]).size().head(
                15
            ).unstack().plot(
                kind="bar",
                ax=ax,
                ylabel="Number of requests",
                xlabel="Remote site, Access limit",
            )
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
            ax.tick_params("x", labelrotation=360)
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
