import nagiosplugin

state_mapping = {
    0: nagiosplugin.Ok,
    1: nagiosplugin.Warn,
    2: nagiosplugin.Critical,
    3: nagiosplugin.Unknown
}

state_messages = {
    0: "Service is up.",
    1: "Potential issue detected, investigate soon.",
    2: "Service is in a critical state. Action needed immediately!",
    3: "Service state is unknown, please check the configuration or logs."
}


class ServiceHealthContext(nagiosplugin.Context):

    def __init__(self, name, custom_description=None):
        super().__init__(name)
        self.custom_description = custom_description

    def evaluate(self, metric, resource):
        """
        Return the correct Nagios state
        """
        return state_mapping.get(metric.value, nagiosplugin.Unknown)

    def describe(self, metric):
        """
        Custom messages for each Nagios state
        """
        if self.custom_description is not None:
            return self.custom_description
        return state_messages.get(metric.value, "Unexpected service status!")

    def performance(self, metric, resource):
        """
        Performance data in Nagios format
        """
        return f"service_status={metric.value}"
