"""
run the game, optionally with profiling ...
"""

import sys

def _run_app(arg):
    from gravbot.app import App
    app = App(arg)
    app.run()

def _print_usage(out):
    out.write('usage: [--profile] [--test]\n')
    out.write('\t--profile : run with python profiling\n')
    out.write('\t--test    : run in test mode\n')

def _complain_about_usage_and_die():
    _print_usage(sys.stderr)
    sys.exit(1)

def _wrap_with_profiling(entry_point, arg):
    """
    run the given argumentless function entry_point using the python profiler

    trap any SystemExits and KeyboardInterrupts so we can
    still spam the profing results to stdout
    """
    def wrapped_entry_point(arg):
        import pstats
        import cProfile
        p = cProfile.Profile()
        def safety_net(entry_point):
            try:
                entry_point(arg)
            except SystemExit:
                pass
            except KeyboardInterrupt:
                pass
        p.runcall(lambda : safety_net(entry_point))
        s = pstats.Stats(p)
        s.sort_stats('cumulative').print_stats(25)
    return wrapped_entry_point


def main():
    options = {
        '--profile': False,
        '--test': False,
    }

    for arg in sys.argv[1:]:
        if arg not in options:
            _complain_about_usage_and_die()
        else:
            options[arg] = True

    apparg = ""
    entry_point = _run_app
    if options['--test']:
        apparg  =  "test"

    if options['--profile']:
        entry_point = _wrap_with_profiling(entry_point, "")

    entry_point(apparg)
    sys.exit(0)

if __name__ == '__main__':
    main()

