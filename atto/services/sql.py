
from atto_api.cdi import activator
from atto_api.source import ISourceType, ISourceTypeGroups


class PostgreSqlSource:
    pass


class MySqlSource:
    pass


@activator
class Databases:
    def start(self, ctx):
        ctx.register_service(ISourceType, PostgreSqlSource(), {
            'group': ISourceTypeGroups.DATABASE,
            'name': 'psql',
            'label': 'PostgreSQL',
            'descripions': 'Database source supporting PostgreSQL connections'
        })

        ctx.register_service(ISourceType, MySqlSource(), {
            'group': ISourceTypeGroups.DATABASE,
            'name': 'mysql',
            'label': 'MySQL',
            'descripions': 'Database source supporting MySQL connections'
        })

    def stop(self, ctx):
        pass
