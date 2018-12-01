Provides a decorator for Luigi tasks that allows them to fail *softly*. Tasks that fail softly are seen by Luigi as complete, and thus don't prevent dependent tasks from running. The dependent task can check if it's dependencies actually ran successfully or failed softly.


# Installation

    pip install luigi_soft_failures


# Usage

```python
from luigi_soft_failures import softly_failing
```

Use as class decorator:

```python
@softly_failing(catch_all=True, propagate=True)
class SomeTask(luigi.Task):
    ...
```

Or on demand in the requiring task:

```python
def requires(self):
    return softly_failing(catch_all=True)(SomeTask)(some_param=42)
```

The dependent task can check the status of it's dependencies using `failed_softly`:

```python
def run(self):
    if self.requires().failed_softly():
        ...
```

For a complete example see [as_decorator.py](https://github.com/maxhollmann/luigi_soft_failures/blob/master/examples/as_decorator.py).


## API

`softly_failing` accepts the following parameters:

* `catch_all` (`bool`, default `False`):

  When `True`, any exception thrown in the task's `run` method will lead to a soft failure. Otherwise, soft failures can be generated manually by calling `self.fail_softly('Some error message')` from the task's `run` method and exiting the method without exception.

* `propagate` (`bool`, default `False`):

  When `True`, the task fails softly if any of it's dependencies failed softly, and `run` is never executed. Otherwise, `run` is executed as if the dependencies ran successfully.

* `output_dir` (`str`, default `None`): Described [below](#storage-of-soft-failure-reports).


## Storage of soft failure reports

Whan the wrapped task fails softly, it creates a report with the failure message or exception traceback to indicate this. These reports are stored in a directory specified in one of the following ways (in this order of precedence):

* `output_dir` parameter passed to `softly_failing`
* Specified in `luigi.cfg`:

      [luigi_soft_failures.Config]
      output_dir=/some/path

* Environment variable `LUIGI_SOFT_FAILURES_OUTPUT_DIR`
* Default `./soft_failures/`


# Limitations

* Soft failure status is stored using a `LocalTarget`, so a local storage that all workers have access to is required.
* In the Luigi visualizer, softly failed tasks are shown as complete.

Pull requests to address these are very welcome!
