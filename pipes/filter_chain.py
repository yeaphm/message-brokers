from pipes.filter import FilterService
from pipes.publish import PublishService
from pipes.screaming import ScreamingService

filter_chain = FilterService(
    next_filter=ScreamingService(
        next_filter=PublishService()
    )
)