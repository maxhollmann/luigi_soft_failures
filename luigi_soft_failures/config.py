import luigi
import os

class Config(luigi.Config):
    task_namespace = 'luigi_soft_failures'

    output_dir = luigi.Parameter(
        default=os.environ.get('LUIGI_SOFT_FAILURES_OUTPUT_DIR', 'soft_failures'))
