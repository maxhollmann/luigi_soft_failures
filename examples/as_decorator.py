import luigi
from random import randint
from luigi_soft_failures import softly_failing


class AggregateTexts(luigi.Task):
    def requires(self):
        return [CreateText(words=n) for n in range(1, 20)]

    def output(self):
        return luigi.LocalTarget('aggregated.txt')

    def run(self):
        with self.output().open("w") as out_f:
            # Iterate over self.requires() instead of self.input(), so
            # that we can check if the task failed softly.
            for dep in self.requires():
                if dep.failed_softly():
                    out_f.write("Failed!\n")
                else:
                    with dep.output().open('r') as text_f:
                        out_f.write(text_f.read() + "\n")


@softly_failing(catch_all=True)
class CreateText(luigi.Task):
    words = luigi.IntParameter()

    def output(self):
        return luigi.LocalTarget('text_{}.txt'.format(self.words))

    def run(self):
        if randint(0, 1) == 1: # Fail randomly
            raise Exception("Something happened!")
        with self.output().open("w") as f:
            f.write("bla " * self.words)


if __name__ == '__main__':
    luigi.build(
        [AggregateTexts()],
        local_scheduler=True)
