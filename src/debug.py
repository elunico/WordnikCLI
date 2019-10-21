def dump_locals(lcls):
    print('|' + ('='*78) + '|')
    print("|Locals:".ljust(79) + '|')
    print('|' + ('- -'*(79//3)) + '|')
    for (k, v) in lcls.items():
        print("|  {} => {}".format(k, v).ljust(79) + '|')
    print('|' + ('='*78) + '|')


def dump_obj(name, obj):
    print('|' + ('='*78) + '|')
    print('|dump of {} (type: {})'.format(name, obj).ljust(79) + '|')
    print('|' + (' - ' * (79//3)) + "|")
    for (k, v) in obj.__dict__.items():
        print("|  {} => {}".format(k, v.__repr__()).ljust(79) + '|')
    print('|' + ('='*78) + '|')
