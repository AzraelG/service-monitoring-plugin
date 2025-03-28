# Service Monitoring Plugin

## Overview

The **Service Monitoring Plugin** is a Python-based monitoring tool for checking the health status of **Elasticsearch, Kibana, and Logstash** services. It uses **Nagios-compatible exit codes** (OK, WARNING, CRITICAL, UNKNOWN) and can be integrated with **Icinga2** for automated service monitoring.

## Features
- Monitors **Elasticsearch, Kibana, and Logstash** health statuses.
- Uses **Nagios exit codes** for structured monitoring.
- Provides **CLI-based** execution for easy use.
- Supports **Icinga2 integration** for automated checks.
- Includes **unit tests** for robust reliability.

## Project Structure

```
service-monitoring-plugin
├── LICENSE
├── src
│   ├── check_services.py
│   ├── __init__.py
│   ├── lib
│   │   ├── config.py
│   │   ├── exceptions.py
│   │   ├── http_driver.py
│   │   ├── __init__.py
│   │   ├── logging_config.py
│   ├── nagios
│   │   ├── __init__.py
│   │   ├── service_health_context.py
│   │   ├── service_health_resource.py
│   ├── README.md
│   └── services
│       ├── base_service.py
│       ├── elasticsearch_service.py
│       ├── __init__.py
│       ├── kibana_service.py
│       ├── logstash_service.py
└── tests
    └── unit
        ├── conftest.py
        ├── test_base_service.py
        ├── test_check_services.py
        ├── test_elasticsearch_service.py
        ├── test_http_driver.py
        ├── test_kibana_service.py
        ├── test_logstash_service.py
        ├── test_nagios_service_health_context.py
        ├── test_nagios_service_health_resource.py
```

## Dependencies

This project uses the following Python libraries:
- **[`nagiosplugin`](https://pypi.org/project/nagiosplugin/)** – Nagios-compatible exit codes.
- **[`requests`](https://pypi.org/project/requests/)** – HTTP API calls.
- **[`click`](https://pypi.org/project/click/)** – CLI support.
- **[`unittest`](https://docs.python.org/3/library/unittest.html)** – Unit testing.
- **[`unittest.mock`](https://docs.python.org/3/library/unittest.mock.html)** – Mock API responses.

## Installation

```sh
# Clone the repository
git clone https://github.com/yourusername/service-monitoring-plugin.git
cd service-monitoring-plugin

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run the service check script with:
```sh
python3 src/check_services.py --service elasticsearch --endpoint https://localhost:9200 --user elastic --password changeme
```
## Health Check Endpoints

| Service          | Endpoint                  | OK           | WARNING     | CRITICAL   | UNKNOWN       |
|-----------------|--------------------------|-------------|------------|------------|--------------|
| Elasticsearch   | `/_health_report`        | `green`     | `yellow`   | `red`      | `unknown`    |
| Kibana         | `/api/status`            | `available` | `degraded` | `critical` | `unavailable` |
| Logstash       | `/_node/stats/process`   | `<70% CPU`  | `70-85%`   | `>85%`     | `No data`    |

## Testing

Run unit tests using:
```sh
pytest tests/unit
```

## Icinga2 Integration

To integrate with **Icinga2**, add a custom command definition:
```sh
object CheckCommand "service_health" {
    command = [ "/usr/bin/python3", "/path/to/check_services.py" ]
    arguments = {
        "--service" = "$service_name$"
    }
}
```

## License

This project is licensed under the [MIT License](LICENSE).

---