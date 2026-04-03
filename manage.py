#!/usr/bin/env python
import os
import sys
from dotenv import load_dotenv

load_dotenv()

env = os.environ.get('ENV', 'local')
settings_map = {
    'local': 'backend.settings.local',
    'development': 'backend.settings.development',
    'stage': 'backend.settings.stage',
    'production': 'backend.settings.production',
}

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_map.get(env, 'backend.settings.local'))
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
