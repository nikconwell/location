# BATS scripts for quick validation

# Initial setup for bats
# (comes from epel)
yum install bats --enablerepo=epel

# Install test helpers
cd tests
git submodule add https://github.com/bats-core/bats-support.git test_helper/bats-support
git submodule add https://github.com/bats-core/bats-assert.git test_helper/bats-assert
