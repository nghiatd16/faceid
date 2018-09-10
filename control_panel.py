import manage_data
import screen
import argparse
import os
import learning

parser = argparse.ArgumentParser(description="")
parser.add_argument("-learn", help="-learn : Delete all experiences and learn new data", dest="learn", action="store")
parser.set_defaults(learn=None)
parser.add_argument("-run", help="-run : Run face recognition system", dest="run", action="store_true")
parser.set_defaults(run=False)
parser.add_argument("--server", help="--server = get image from server", dest="server", action="store")
parser.set_defaults(server= None)

def main(args):
    if args.learn is not None:
        learning.offline_learning(args.learn)
    if args.run == True:
        if args.server == None:
            screen.run()
        else:
            screen.run(args.server)

if __name__ == '__main__':
    main(parser.parse_args())