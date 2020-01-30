from spidermon.contrib.actions.telegram.notifiers import (
    SendTelegramMessageSpiderFinished,
)
from spidermon.contrib.scrapy.monitors import ErrorCountMonitor, FinishReasonMonitor
from spidermon.core.suites import MonitorSuite


class SpiderCloseMonitorSuite(MonitorSuite):
    monitors = [
        ErrorCountMonitor,
        FinishReasonMonitor,
    ]

    monitors_finished_actions = [
        SendTelegramMessageSpiderFinished,
    ]

    monitors_failed_actions = [
        SendTelegramMessageSpiderFinished,
    ]
