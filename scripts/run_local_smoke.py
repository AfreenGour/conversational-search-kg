import traceback
from tests.test_smoke import test_flow


def main():
    try:
        test_flow()
        print('LOCAL SMOKE: PASS')
    except AssertionError as e:
        print('LOCAL SMOKE: FAIL - assertion error:', e)
        traceback.print_exc()
        raise
    except Exception as e:
        print('LOCAL SMOKE: ERROR')
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main()
