from spidermon import Monitor, MonitorSuite, monitors
from spidermon.contrib.actions.telegram import SendTelegramMessage
from spidermon.contrib.scrapy.monitors import (
    ErrorCountMonitor,
    FinishReasonMonitor,
    ItemValidationMonitor,
)


def find_exceptions(stats):
    exceptions = []
    for key, value in stats.items():
        if key.startswith("spider_exceptions"):
            exceptions.append(f"{key} ({value})")
    return exceptions


@monitors.name("Taxa requests/itens")
class RequestsItemsRatioMonitor(Monitor):
    @monitors.name("Taxa de requests por itens raspados")
    def test_requests_items_ratio(self):
        n_scraped_items = self.data.stats.get("item_scraped_count", 0)
        n_requests_count = self.data.stats.get("downloader/request_count", 0)
        max_ratio = 10

        if n_scraped_items > 0:
            ratio = n_requests_count / n_scraped_items
            percent = round(ratio * 100, 2)
            allowed_percent = round(max_ratio * 100, 2)
            self.assertLess(
                ratio,
                max_ratio,
                msg=f"""{percent}% é maior que {allowed_percent}%
                da taxa de requests por itens raspados.
                """,
            )


class CustomSendTelegramMessage(SendTelegramMessage):
    def get_message(self):
        stats = self.data.stats
        n_scraped_items = stats.get("item_scraped_count", 0)

        failures = len(self.result.failures)
        emoji = "💀" if failures > 0 else "🎉"

        exceptions = find_exceptions(stats)
        exceptions_message = ""
        if exceptions:
            exceptions_message = "\n".join(exceptions)

        message = "\n".join(
            [
                f"{emoji} Spider {self.data.spider.name} {stats['finish_reason']}",
                f"- Duração em segundos: {stats['elapsed_time_seconds']}",
                f"- Itens raspados: {n_scraped_items}",
                f"- Erros: {failures}\n{exceptions_message}",
            ]
        )
        return message


class SpiderCloseMonitorSuite(MonitorSuite):

    monitors = [
        RequestsItemsRatioMonitor,
        ErrorCountMonitor,
        FinishReasonMonitor,
        ItemValidationMonitor,
    ]

    monitors_finished_actions = [CustomSendTelegramMessage]
