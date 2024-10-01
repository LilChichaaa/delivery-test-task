from dynaconf import Dynaconf

settings = Dynaconf(settings_files=['.env', 'config.json'])

