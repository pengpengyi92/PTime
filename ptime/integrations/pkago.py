"""Generic P Kago placeholder: normalized local data only; native contract unknown."""

from ptime.integrations.base import LocalCommunicationSource


class PKagoSource(LocalCommunicationSource):
    source_name = "pkago_communication_export"
