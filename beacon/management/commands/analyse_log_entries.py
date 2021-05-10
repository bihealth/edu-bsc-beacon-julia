from django.core.management.base import BaseCommand, CommandError
from beacon.models import LogEntry, RemoteSite
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt


class Command(BaseCommand):
    help = 'Creates a statistical overview about the logged requests'

    def add_arguments(self, parser):
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
        plt.style.use('seaborn-bright')
        if options["path"]:
            path = options["path"]
            try:
                os.chdir(path)
            except OSError:
                return self.stderr.write(self.style.ERROR("Couldn't find the directory or permission for the directory is missing: " + path))
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
        for l in LogEntry.objects.all()[len(LogEntry.objects.all()) - 13:]:  # TODO: all again
            method, endpoint, reference, alternative, chromosome, start, end, release = self._read_in_request(
                l.request)
            methods.append(method)
            endpoints.append(endpoint)
            user_identifiers.append(l.user_identifier)
            ip_addresses.append(l.ip_address)
            if l.authuser_id is None:
                authuser_names.append(None)
            else:
                authuser_names.append(RemoteSite.objects.get(id=l.authuser_id).name)
            date_times.append(l.date_time)
            status_codes.append(l.status_code)
            response_sizes.append(l.response_size)
            references.append(reference)
            alternatives.append(alternative)
            chromosomes.append(chromosome)
            starts.append(start)
            ends.append(end)
            releases.append(release)
        log_data = pd.DataFrame(data={"method": methods,
                                      "endpoint": endpoints,
                                      "user_identifier": user_identifiers,
                                      "ip_address": ip_addresses,
                                      "authuser_name": authuser_names,
                                      "date_time": [pd.to_datetime(d).tz_localize(None) for d in date_times], #time zone removed
                                      "status_code": status_codes,
                                      "response_size": response_sizes,
                                      "reference": references,
                                      "alternative": alternatives,
                                      "chromosome": chromosomes,
                                      "start": starts,
                                      "end": ends,
                                      "release": releases})
        if options["as_csv"]:
            log_data.to_csv("log_entry_data.csv")
        log_data_indexed = log_data.set_index("date_time")
        if options["time_period"]:
            try:
                time_start = pd.to_datetime(options["time_period"][0])
                time_end = pd.to_datetime(options["time_period"][1])
                if time_start > time_end:
                    raise Exception
            except Exception:
                return self.stderr.write(self.style.ERROR("Your input format of the date_time is invalid."))
            log_data_indexed = log_data_indexed.loc[time_start:time_end]
            if log_data_indexed.empty:
                return self.stdout.write(self.style.WARNING("WARNING: No data available for the given time period."))
        fig, ax = plt.subplots(figsize=(15, 7)) #TODO: headlines for all plots, label="Number of request per endpoint"
        #log_data_indexed.groupby([log_data_indexed.index.year, log_data_indexed.index.month, "endpoint"]).size().unstack().plot(kind='bar', ax=ax, ylabel="Number of requests", xlabel="Time period")
        log_data_indexed.groupby([log_data_indexed.index.year, log_data_indexed.index.month, log_data_indexed.index.day, "authuser_name"]).size().unstack().plot(kind='line', ax=ax, ylabel="Number of requests", xlabel="Time period", ylim=(0, 10000))
        if options["path"]:
            plt.savefig("calls_per_endpoint.pdf")
            if options["as_csv"]:
                try:
                    log_data.to_csv("log_entry_data.csv")
                except OSError:
                    return self.stderr.write(self.style.ERROR("You have no writing permission for the current directory." ))
        else:
            plt.show()
            if options["as_csv"]:
                try:
                    log_data.to_csv("log_entry_data.csv")
                    self.stdout.write(self.style.WARNING("WARNING: The log_entry_data.csv file was saved in the current working directory."))
                except OSError:
                    return self.stderr.write(self.style.ERROR("You have no writing permission for the current directory." ))
        return self.stdout.write(self.style.SUCCESS("A statistical overview of the logged requests was created successfully."))

    def _read_in_request(self, request_field):
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
