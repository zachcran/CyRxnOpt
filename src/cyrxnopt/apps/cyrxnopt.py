import argparse
import sys

from cyrxnopt.apps import (
    configure_optimizer,
    create_config,
    install_optimizer,
    start_optimization,
    train_optimizer,
)


def main(args: argparse.Namespace) -> int:
    args.func(args)

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="cyrxnopt")

    subparsers = parser.add_subparsers(title="Subcommands", required=True)

    install_parser = install_optimizer.get_parser(
        lambda *args, **kwargs: subparsers.add_parser(
            "install", *args, **kwargs
        )
    )
    install_parser.set_defaults(func=install_optimizer.main)

    create_config_parser = create_config.get_parser(
        lambda *args, **kwargs: subparsers.add_parser(
            "config-init", *args, **kwargs
        )
    )
    create_config_parser.set_defaults(func=create_config.main)

    configure_parser = configure_optimizer.get_parser(
        lambda *args, **kwargs: subparsers.add_parser("config", *args, **kwargs)
    )
    configure_parser.set_defaults(func=configure_optimizer.main)

    train_parser = train_optimizer.get_parser(
        lambda *args, **kwargs: subparsers.add_parser("train", *args, **kwargs)
    )
    train_parser.set_defaults(func=train_optimizer.main)

    predict_parser = start_optimization.get_parser(
        lambda *args, **kwargs: subparsers.add_parser(
            "predict", *args, **kwargs
        )
    )
    predict_parser.set_defaults(func=start_optimization.main)

    return parser.parse_args()


def run() -> int:
    return main(parse_args())


if __name__ == "__main__":
    sys.exit(run())
