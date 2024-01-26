import sys, argparse, math

parser = argparse.ArgumentParser(description="Uses a trained network to detect object in images")
parser.add_argument('-s', '--sethome', type=int, required=False,
                    help='run set home.')
args = parser.parse_args()


class foo:
    def __init__(self, a):
        self.a = a
        print(f"cc {a}")

    def __enter__(self,*arg):
        print(f"bb {arg}")
        return self

    def __exit__(self, c, *arg):
        print(f"cc {c}, arg {arg}")

with foo(args.sethome) as d:
    print(d.a)