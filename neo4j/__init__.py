class _Tx:
    def run(self, *args, **kwargs):
        raise RuntimeError("neo4j stub: no DB available in editor. Install official 'neo4j' package to use real DB.")


class _Session:
    def begin_transaction(self):
        return _Tx()

    def run(self, *args, **kwargs):
        raise RuntimeError("neo4j stub: no DB available in editor. Install official 'neo4j' package to use real DB.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class GraphDatabase:
    @staticmethod
    def driver(*args, **kwargs):
        class _Driver:
            def session(self):
                return _Session()

        return _Driver()
