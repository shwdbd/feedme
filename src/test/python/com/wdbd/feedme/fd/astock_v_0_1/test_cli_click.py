import click
import unittest
from click.testing import CliRunner


@click.command()
@click.option('--foo')
def hello(foo):
    click.echo('foo=%s' % foo)


def test_hello_world():
    runner = CliRunner()
    result = runner.invoke(hello, ['--foo', 'Peter'])
    print(result)
    print(result.exit_code)
    print(result.output)
    # assert(result.exit_code == 0)
    # assert result.output == 'Hello Peter!\n'


class TestClick(unittest.TestCase):
    
    def test_click(self):
        runner = CliRunner()
        result = runner.invoke(hello, ['Peter'])
        print(result)


if __name__ == "__main__":
    test_hello_world()


# if __name__ == "__main__":
#     # hello()
#     runner = CliRunner()
#     result = runner.invoke(hello, ['Peter'])
