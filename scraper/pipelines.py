from scraper.spiders.utils import get_git_commit


class DefaultValuesPipeline(object):
    def process_item(self, item, spider):
        item.setdefault("git_commit", get_git_commit())
        return item
