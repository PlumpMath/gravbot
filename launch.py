"""
run the game, optionally with profiling ...
"""

import sys

def _run_app():
    from gravbot.app import App
    app = App()
    app.run()

def _run_test_app():
    from gravbot.mc import App
    app = App()
    app.run()

def _print_usage(out):
    out.write('usage: [--profile] [--test]\n')
    out.write('\t--profile : run with python profiling\n')
    out.write('\t--test    : run in test mode (mc.py)\n')

def _complain_about_usage_and_die():
    _print_usage(sys.stderr)
    sys.exit(1)

def _wrap_with_profiling(entry_point):
    """
    run the given argumentless function entry_point using the python profiler

    trap any SystemExits and KeyboardInterrupts so we can
    still spam the profing results to stdout
    """
    def wrapped_entry_point():
        import pstats
        import cProfile
        p = cProfile.Profile()
        def safety_net(entry_point):
            try:
                entry_point()
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

    if options['--test']:
        entry_point = _run_test_app
    else:
        entry_point = _run_app

    if options['--profile']:
        entry_point = _wrap_with_profiling(entry_point)

    entry_point()
    sys.exit(0)

if __name__ == '__main__':
    main()

