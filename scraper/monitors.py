from spidermon import MonitorSuite
from spidermon.contrib.actions.telegram import SendTelegramMessage
from spidermon.contrib.scrapy.monitors import FinishReasonMonitor, ItemValidationMonitor


def find_exceptions(stats):
    exceptions = []
    for key, value in stats.items():
        if key.startswith("spider_exceptions"):
            exceptions.append(f"`{key}` ({value})")
        elif key.startswith("downloader/response_status_count/4"):
            exceptions.append(f"Página não encontrada ({value})")
    return exceptions


class CustomSendTelegramMessage(SendTelegramMessage):
    def get_message(self):
        stats = self.data.stats
        n_scraped_items = stats.get("item_scraped_count", 0)

        exceptions = find_exceptions(stats)
        exceptions_message = ""
        if exceptions:
            exceptions_message = "\n".join(exceptions)

        number_of_failures = len(self.result.failures)
        number_of_exceptions = len(exceptions)
        emoji = "💀" if number_of_failures > 0 or number_of_exceptions > 0 else "🎉"

        message = "\n".join(
            [
                f"{emoji} Spider `{self.data.spider.name}` {stats['finish_reason']}",
                f"- Duração em segundos: {stats['elapsed_time_seconds']}",
                f"- Itens raspados: {n_scraped_items}",
                f"- Erros: {number_of_failures}",
                f"- Exceções: {number_of_exceptions}\n{exceptions_message}",
            ]
        )
        return message


class SpiderCloseMonitorSuite(MonitorSuite):

    monitors = [
        FinishReasonMonitor,
        ItemValidationMonitor,
    ]

    monitors_finished_actions = [CustomSendTelegramMessage]
