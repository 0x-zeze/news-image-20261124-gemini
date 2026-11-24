"""Deterministic entrypoint: generates /output/entry.png (1024x1024, stdlib only)."""

from draw import render


def main():
    render("/output/entry.png")


if __name__ == "__main__":
    main()
