import logging

class IPAddressFilter(logging.Filter):

    def filter(self, record):
        if hasattr(record, 'request'):
            print(record.request.Headers)
            x_forwarded_for = record.request.headers('X-Forwarded-For')
            if x_forwarded_for:
                record.ip = x_forwarded_for.split(',')[0]
            else:
                record.ip = record.request.META.get('REMOTE_ADDR')
                
        return True
    
    
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
        "default": {
            # "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            "format": "[%(asctime)s] :  - %(name)s - %(ip)s - %(levelname)s -  %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "logs/access.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        },
        "vmware": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "level": "WARNING",
            "level": "INFO",
            "formatter": "simple",
            "filename": "logs/vmware.log",
            "maxBytes": 10485760,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },
    'filters': {
        'add_ip_address': {
            '()': 'app.logger.IPAddressFilter' # You can move IPAddressFilter class from settings.py to another location (e.g., apps.other.filters.IPAddressFilter)
        }
    },
    "loggers": {
        "vmware" : {
                "level": "DEBUG",
                "handlers": ["vmware"]
        }     
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "info_file_handler", "error_file_handler"]
    }
}


def load_logging():
    import logging.config
    logging.config.dictConfig(LOGGING)