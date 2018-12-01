import luigi
import traceback
from luigi_soft_failures.config import Config
from luigi_soft_failures.utils import ensure_dir


class softly_failing:
    """Decorator to allow a Luigi task to fail softly.

    Args:
        catch_all (bool): Fail softly when the `run` method throws any exception.
        propagate (bool): Fail softly when any dependency failed softly.
        output_dir (str): Directory in which to store soft failure reports.
    """
    def __init__(self, catch_all=False, propagate=False, output_dir=None):
        self._catch_all = catch_all
        self._propagate = propagate
        self._output_dir = output_dir

    def __call__(self_, task):
        """Wrap the task."""
        @luigi.task._task_wraps(task)
        class Wrapped(task):
            def run(self):
                if self_._propagate:
                    failed_deps = [t for t in self.deps() if t.failed_softly()]
                    if any(failed_deps):
                        msg = "Propagated soft failure from:\n\n"
                        msg += "\n\n=========\n\n".join(
                            [t.output(failed=True)._propagated_failure_message_part()
                             for t in failed_deps])
                        self.fail_softly(msg)
                        return

                try:
                    super().run()
                except Exception as e:
                    if self_._catch_all:
                        self.fail_softly(e)
                    else:
                        raise


            def fail_softly(self, exception_or_msg="failed"):
                if isinstance(exception_or_msg, Exception):
                    msg = ''.join(
                        traceback.format_exception(
                            etype=type(exception_or_msg),
                            value=exception_or_msg,
                            tb=exception_or_msg.__traceback__))
                else:
                    msg = exception_or_msg

                with self.output(failed=True).open("w") as f:
                    f.write(msg)

            def failed_softly(self):
                return self.output(failed=True).exists()


            def complete(self):
                return super().complete() or self.failed_softly()

            def output(self, failed=False):
                if failed:
                    if self_._output_dir:
                        output_dir = self_._output_dir
                    else:
                        output_dir = Config().output_dir
                    return SoftFailureTarget(self.task_id, output_dir=output_dir)
                else:
                    return super().output()


        return Wrapped


class SoftFailureTarget(luigi.LocalTarget):
    def __init__(self, task_id, output_dir):
        self._task_id = task_id
        self._task_fam = task_id.split("_", 1)[0]
        path = ensure_dir(output_dir, self._task_fam, self._task_id)
        super().__init__(path)


    def _propagated_failure_message_part(self):
        if self._propagated():
            upstream_id = self._propagated_from()
            part2 = SoftFailureTarget(upstream_id)._propagated_failure_message_part()
        else:
            part2 = "\n{}".format(self._content().strip())
        return "-> {}\n{}".format(self._task_id, part2)

    def _propagated(self):
        return self._content().startswith("Propagated soft failure from")

    def _propagated_from(self):
        return self._content().split("\n")[2][3:]

    def _content(self):
        with self.open('r') as f:
            return f.read()
