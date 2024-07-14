function setup() {
    load 'test_helper/bats-support/load'
    load 'test_helper/bats-assert/load'

    # get the containing directory of this file
    # use $BATS_TEST_FILENAME instad of ${BASH_SOURCE[0]} or $0,
    # as those will point to the bats executable's location or the preprocessed file respectively
    DIR="$( cd "$( dirname "$BATS_TEST_FILENAME" )" >/dev/null 2>&1 && pwd )"
    PATH="$DIR/..:$PATH"
}

# function setup_file() {
#     # Start a daemon for REST testing
#     ./fuzzy.py --rest :5001 &
#     fuzzypid=$!
# }


# function teardown_file() {
#     kill ${fuzzypid}
# }


@test "Pull out basic log information: parselog.py --input log.pdf | head" {
    run bash -c "parselog.py --input log.pdf | head"
    assert_output --partial '2024/01/01 13:21:00,171 HARTFORD ST'
}

@test "Pull out basic log information: parselog.py --input log.pdf | tail" {
    run bash -c "parselog.py --input log.pdf | tail"
    assert_output --partial '2024/01/06 20:28:00,1245 WORCESTER ST'
}



