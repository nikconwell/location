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



@test "Run with basic address 172 HARTFORD ST natick ma" {
    run convert.py '172 HARTFORD ST natick ma'
    assert_output --partial 'Latitude = 42.291410'
    assert_output --partial 'Longitude = -71.398049'
}

@test "Run with basic address 1245 WORCESTER ST natick ma" {
    run convert.py '1245 WORCESTER ST natick ma'
    assert_output --partial 'Latitude = 42.300226'
    assert_output --partial 'Longitude = -71.383479'
}

@test "Check town addition 1245 WORCESTER ST" {
    run convert.py '1245 WORCESTER ST'
    assert_output --partial 'Added in town'
    assert_output --partial 'Latitude = 42.300226'
    assert_output --partial 'Longitude = -71.383479'
}
