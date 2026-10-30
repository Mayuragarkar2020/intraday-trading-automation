"""Safe entrypoint: data ingestion and restriction validation not yet implemented."""
import sys


def main() -> int:
    print('NOT_READY: NSE source adapters and screening validation are not implemented.', file=sys.stderr)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
